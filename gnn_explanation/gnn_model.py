import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool
from torch_geometric.data import Data, DataLoader
import numpy as np

class StudentBehaviorGNN(nn.Module):
    """学生行为GNN模型"""
    
    def __init__(self, input_dim, hidden_dim, output_dim, model_type='gcn', heads=4):
        super(StudentBehaviorGNN, self).__init__()
        self.model_type = model_type
        self.heads = heads
        
        if model_type == 'gcn':
            # GCN模型
            self.conv1 = GCNConv(input_dim, hidden_dim)
            self.conv2 = GCNConv(hidden_dim, hidden_dim)
            self.conv3 = GCNConv(hidden_dim, output_dim)
        elif model_type == 'gat':
            # GAT模型
            self.conv1 = GATConv(input_dim, hidden_dim, heads=heads)
            self.conv2 = GATConv(hidden_dim * heads, hidden_dim, heads=heads)
            self.conv3 = GATConv(hidden_dim * heads, output_dim, heads=1)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 分类层
        self.fc = nn.Linear(output_dim, 4)  # 4个类别：正常、预警、告警、严重告警
    
    def forward(self, data):
        x, edge_index, batch = data.x, data.edge_index, data.batch
        
        if self.model_type == 'gcn':
            x = F.relu(self.conv1(x, edge_index))
            x = F.dropout(x, p=0.5, training=self.training)
            x = F.relu(self.conv2(x, edge_index))
            x = F.dropout(x, p=0.5, training=self.training)
            x = self.conv3(x, edge_index)
        elif self.model_type == 'gat':
            x = F.relu(self.conv1(x, edge_index))
            x = F.dropout(x, p=0.5, training=self.training)
            x = F.relu(self.conv2(x, edge_index))
            x = F.dropout(x, p=0.5, training=self.training)
            x = self.conv3(x, edge_index)
            x = x.squeeze(dim=1)
        
        # 图级别池化
        x = global_mean_pool(x, batch)
        
        # 分类
        x = self.fc(x)
        
        return x

class StudentGraphData:
    """学生行为图数据构建"""
    
    def __init__(self):
        self.student_features = {}
        self.edge_index = []
        self.edge_attr = []
    
    def add_student_node(self, student_id, features):
        """添加学生节点"""
        self.student_features[student_id] = features
    
    def add_edge(self, src_id, dst_id, edge_type='interaction', weight=1.0):
        """添加边"""
        src_idx = list(self.student_features.keys()).index(src_id)
        dst_idx = list(self.student_features.keys()).index(dst_id)
        self.edge_index.append([src_idx, dst_idx])
        self.edge_attr.append({'type': edge_type, 'weight': weight})
    
    def build_graph(self):
        """构建图数据"""
        # 构建节点特征矩阵
        node_features = []
        for student_id, features in self.student_features.items():
            node_features.append(features)
        
        x = torch.tensor(np.array(node_features), dtype=torch.float)
        
        # 构建边索引
        edge_index = torch.tensor(self.edge_index, dtype=torch.long).t().contiguous()
        
        # 构建边属性
        edge_weights = [attr['weight'] for attr in self.edge_attr]
        edge_attr = torch.tensor(edge_weights, dtype=torch.float).view(-1, 1)
        
        # 创建图数据
        data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)
        
        return data

def create_student_behavior_graph(student_data, behavior_representations):
    """创建学生行为图"""
    graph_builder = StudentGraphData()
    
    # 添加学生节点
    for student_id, features in behavior_representations.items():
        graph_builder.add_student_node(student_id, features)
    
    # 添加边（基于相似度）
    student_ids = list(behavior_representations.keys())
    for i in range(len(student_ids)):
        for j in range(i + 1, len(student_ids)):
            # 计算行为相似度
            sim = np.dot(behavior_representations[student_ids[i]], 
                        behavior_representations[student_ids[j]])
            if sim > 0.3:  # 相似度阈值
                graph_builder.add_edge(student_ids[i], student_ids[j], 'similarity', sim)
    
    return graph_builder.build_graph()

def train_gnn_model(model, dataloader, optimizer, criterion, epochs=100):
    """训练GNN模型"""
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for data in dataloader:
            optimizer.zero_grad()
            out = model(data)
            loss = criterion(out, data.y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}')
    
    return model

def evaluate_gnn_model(model, dataloader):
    """评估GNN模型"""
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data in dataloader:
            out = model(data)
            pred = out.argmax(dim=1)
            correct += int((pred == data.y).sum())
            total += data.y.size(0)
    
    accuracy = correct / total
    print(f'模型准确率: {accuracy:.4f}')
    return accuracy