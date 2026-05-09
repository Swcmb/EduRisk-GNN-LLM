import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class Encoder(nn.Module):
    """编码器网络 - 将输入特征映射到潜在空间"""
    def __init__(self, input_dim, hidden_dim=128, output_dim=64):
        super(Encoder, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.2)
        
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.bn2 = nn.BatchNorm1d(hidden_dim)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        
        x = self.fc2(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        
        x = self.fc3(x)
        return x

class ProjectionHead(nn.Module):
    """投影头 - 将编码器输出映射到对比学习空间"""
    def __init__(self, input_dim=64, hidden_dim=32, output_dim=16):
        super(ProjectionHead, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

class SimCLR(nn.Module):
    """SimCLR模型 - 自监督对比学习框架"""
    def __init__(self, input_dim, encoder_hidden_dim=128, encoder_output_dim=64, 
                 projection_hidden_dim=32, projection_output_dim=16):
        super(SimCLR, self).__init__()
        
        # 编码器网络
        self.encoder = Encoder(
            input_dim=input_dim,
            hidden_dim=encoder_hidden_dim,
            output_dim=encoder_output_dim
        )
        
        # 投影头
        self.projection_head = ProjectionHead(
            input_dim=encoder_output_dim,
            hidden_dim=projection_hidden_dim,
            output_dim=projection_output_dim
        )
    
    def forward(self, x):
        """前向传播 - 返回编码器输出和投影输出"""
        # 通过编码器获取表征
        representation = self.encoder(x)
        
        # 通过投影头获取对比学习空间的表示
        projection = self.projection_head(representation)
        
        return representation, projection
    
    def get_representation(self, x):
        """获取编码器的输出（表征向量）"""
        with torch.no_grad():
            representation = self.encoder(x)
        return representation
    
    def get_projection(self, x):
        """获取投影头的输出（对比学习空间表示）"""
        with torch.no_grad():
            representation = self.encoder(x)
            projection = self.projection_head(representation)
        return projection

class NTXentLoss(nn.Module):
    """NT-Xent损失函数 - 对比学习的核心损失"""
    def __init__(self, temperature=0.5):
        super(NTXentLoss, self).__init__()
        self.temperature = temperature
        self.cross_entropy = nn.CrossEntropyLoss(reduction='sum')
        self.similarity_fn = nn.CosineSimilarity(dim=2)
    
    def forward(self, z_i, z_j):
        """
        计算NT-Xent损失
        z_i: 第一个增强视图的投影
        z_j: 第二个增强视图的投影
        """
        batch_size = z_i.shape[0]
        
        # 将两个视图的投影拼接
        z = torch.cat([z_i, z_j], dim=0)
        
        # 计算余弦相似度矩阵
        similarity = self.similarity_fn(z.unsqueeze(1), z.unsqueeze(0))
        
        # 计算正样本对的掩码
        positive_mask = torch.zeros((2 * batch_size, 2 * batch_size), dtype=torch.bool, device=z.device)
        positive_mask[:batch_size, batch_size:] = torch.eye(batch_size, device=z.device)
        positive_mask[batch_size:, :batch_size] = torch.eye(batch_size, device=z.device)
        
        # 计算负样本对的掩码（排除对角线和正样本）
        negative_mask = ~positive_mask
        negative_mask.fill_diagonal_(0)
        
        # 计算所有样本对的相似度
        logits = similarity / self.temperature
        
        # 对于每个样本，构建分类问题：正样本为目标
        labels = torch.arange(batch_size, device=z.device)
        
        # 计算损失：将z_i与所有样本（包括z_j）进行比较
        loss_i = self.cross_entropy(logits[:batch_size], labels)
        loss_j = self.cross_entropy(logits[batch_size:], labels)
        
        # 平均损失
        loss = (loss_i + loss_j) / (2 * batch_size)
        
        return loss

class SimCLRTrainer:
    """SimCLR训练器"""
    def __init__(self, model, optimizer, loss_fn, device='cpu'):
        self.model = model
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.device = device
        self.model.to(device)
    
    def train_step(self, x_i, x_j):
        """单步训练"""
        self.model.train()
        self.optimizer.zero_grad()
        
        # 将数据移到设备上
        x_i = torch.tensor(x_i, dtype=torch.float32, device=self.device)
        x_j = torch.tensor(x_j, dtype=torch.float32, device=self.device)
        
        # 前向传播
        _, z_i = self.model(x_i)
        _, z_j = self.model(x_j)
        
        # 计算损失
        loss = self.loss_fn(z_i, z_j)
        
        # 反向传播
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def train_epoch(self, dataloader, augmentation_fn):
        """训练一个epoch"""
        total_loss = 0.0
        total_steps = 0
        
        for batch in dataloader:
            # 对每个样本创建两个增强视图
            x_i = augmentation_fn(batch)
            x_j = augmentation_fn(batch)
            
            # 训练步骤
            loss = self.train_step(x_i, x_j)
            
            total_loss += loss
            total_steps += 1
        
        return total_loss / total_steps if total_steps > 0 else 0
    
    def save_model(self, save_path):
        """保存模型"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, save_path)
        print(f"模型已保存到: {save_path}")
    
    def load_model(self, load_path):
        """加载模型"""
        checkpoint = torch.load(load_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        print(f"模型已从: {load_path} 加载")
    
    def get_representations(self, X):
        """获取批量数据的表征向量"""
        self.model.eval()
        X_tensor = torch.tensor(X, dtype=torch.float32, device=self.device)
        
        with torch.no_grad():
            representations = self.model.get_representation(X_tensor)
        
        return representations.cpu().numpy()

class IncrementalLearner:
    """增量学习器"""
    def __init__(self, model, optimizer, loss_fn, device='cpu'):
        self.model = model
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.device = device
        self.model.to(device)
    
    def incremental_update(self, new_data, augmentation_fn, num_epochs=5):
        """增量更新模型"""
        self.model.train()
        
        for epoch in range(num_epochs):
            epoch_loss = 0.0
            batch_size = 32
            
            # 批量处理新数据
            for i in range(0, len(new_data), batch_size):
                batch = new_data[i:i + batch_size]
                
                # 创建增强视图
                x_i = augmentation_fn(batch)
                x_j = augmentation_fn(batch)
                
                # 将数据移到设备上
                x_i_tensor = torch.tensor(x_i, dtype=torch.float32, device=self.device)
                x_j_tensor = torch.tensor(x_j, dtype=torch.float32, device=self.device)
                
                # 前向传播
                _, z_i = self.model(x_i_tensor)
                _, z_j = self.model(x_j_tensor)
                
                # 计算损失
                loss = self.loss_fn(z_i, z_j)
                
                # 反向传播（使用较小的学习率进行微调）
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / (len(new_data) / batch_size)
            print(f"增量学习 epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}")
        
        return avg_loss
    
    def warm_start_training(self, initial_data, augmentation_fn, num_epochs=10):
        """热身训练 - 使用初始数据训练模型"""
        self.model.train()
        
        for epoch in range(num_epochs):
            epoch_loss = 0.0
            batch_size = 32
            
            # 打乱数据
            np.random.shuffle(initial_data)
            
            for i in range(0, len(initial_data), batch_size):
                batch = initial_data[i:i + batch_size]
                
                # 创建增强视图
                x_i = augmentation_fn(batch)
                x_j = augmentation_fn(batch)
                
                # 将数据移到设备上
                x_i_tensor = torch.tensor(x_i, dtype=torch.float32, device=self.device)
                x_j_tensor = torch.tensor(x_j, dtype=torch.float32, device=self.device)
                
                # 前向传播
                _, z_i = self.model(x_i_tensor)
                _, z_j = self.model(x_j_tensor)
                
                # 计算损失
                loss = self.loss_fn(z_i, z_j)
                
                # 反向传播
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / (len(initial_data) / batch_size)
            print(f"热身训练 epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}")
        
        return avg_loss