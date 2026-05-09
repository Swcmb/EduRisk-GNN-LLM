import torch
import torch.nn.functional as F
import numpy as np
from torch_geometric.nn import GNNExplainer
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score

class GNNExplanationSystem:
    """GNN可解释性系统"""
    
    def __init__(self, model, device='cpu'):
        self.model = model
        self.device = device
        self.explainer = GNNExplainer(model, epochs=200, lr=0.01)
    
    def explain_node(self, data, node_idx):
        """解释节点预测"""
        node_feat_mask, edge_mask = self.explainer.explain_node(node_idx, data.x, data.edge_index)
        
        return {
            'node_feat_mask': node_feat_mask.detach().cpu().numpy(),
            'edge_mask': edge_mask.detach().cpu().numpy(),
            'node_idx': node_idx
        }
    
    def explain_graph(self, data):
        """解释图级预测"""
        # 对于图级预测，我们解释所有节点
        explanations = []
        for node_idx in range(data.x.shape[0]):
            try:
                explanation = self.explain_node(data, node_idx)
                explanations.append(explanation)
            except Exception as e:
                print(f"解释节点 {node_idx} 时出错: {e}")
        
        return explanations
    
    def get_key_subgraph(self, data, explanation, threshold=0.5):
        """提取关键子图"""
        edge_mask = explanation['edge_mask']
        node_idx = explanation['node_idx']
        
        # 筛选重要的边
        important_edges = []
        for i, mask in enumerate(edge_mask):
            if mask > threshold:
                edge = data.edge_index[:, i].cpu().numpy()
                important_edges.append((edge[0], edge[1], mask))
        
        # 构建关键子图
        subgraph_edges = [(u, v) for u, v, _ in important_edges]
        subgraph_nodes = set()
        for u, v in subgraph_edges:
            subgraph_nodes.add(u)
            subgraph_nodes.add(v)
        subgraph_nodes.add(node_idx)
        
        return {
            'nodes': list(subgraph_nodes),
            'edges': subgraph_edges,
            'edge_weights': {f"{u}-{v}": w for u, v, w in important_edges},
            'target_node': node_idx
        }
    
    def visualize_explanation(self, data, explanation, title="GNN解释可视化"):
        """可视化解释结果"""
        # 创建NetworkX图
        G = nx.Graph()
        
        # 添加节点
        for i in range(data.x.shape[0]):
            G.add_node(i)
        
        # 添加边并设置权重
        edge_mask = explanation['edge_mask']
        for i in range(data.edge_index.shape[1]):
            u, v = data.edge_index[:, i].cpu().numpy()
            weight = edge_mask[i]
            G.add_edge(u, v, weight=weight)
        
        # 绘制图
        plt.figure(figsize=(10, 8))
        
        # 根据边权重设置颜色
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        
        # 使用spring布局
        pos = nx.spring_layout(G)
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_size=300, node_color='lightblue')
        
        # 绘制边，权重越高颜色越深
        nx.draw_networkx_edges(G, pos, edgelist=edges, width=2,
                              edge_color=weights, edge_cmap=plt.cm.Blues,
                              alpha=0.7)
        
        # 绘制节点标签
        nx.draw_networkx_labels(G, pos, font_size=10)
        
        plt.title(title)
        plt.colorbar(plt.cm.ScalarMappable(cmap=plt.cm.Blues), 
                    ax=plt.gca(), label='边重要性')
        plt.axis('off')
        
        return plt
    
    def evaluate_explanation_quality(self, data, explanations, true_labels):
        """评估解释质量"""
        metrics = {}
        
        # 计算节点特征重要性的统计信息
        all_node_masks = []
        for exp in explanations:
            all_node_masks.append(exp['node_feat_mask'])
        
        node_masks_array = np.array(all_node_masks)
        metrics['mean_node_importance'] = np.mean(node_masks_array)
        metrics['std_node_importance'] = np.std(node_masks_array)
        metrics['max_node_importance'] = np.max(node_masks_array)
        
        # 计算边重要性的统计信息
        all_edge_masks = []
        for exp in explanations:
            all_edge_masks.extend(exp['edge_mask'])
        
        edge_masks_array = np.array(all_edge_masks)
        metrics['mean_edge_importance'] = np.mean(edge_masks_array)
        metrics['std_edge_importance'] = np.std(edge_masks_array)
        metrics['max_edge_importance'] = np.max(edge_masks_array)
        
        # 计算稀疏性指标（重要性大于阈值的比例）
        threshold = 0.5
        metrics['sparsity'] = np.sum(edge_masks_array > threshold) / len(edge_masks_array)
        
        return metrics
    
    def generate_explanation_report(self, data, explanations, student_ids):
        """生成解释报告"""
        report = []
        
        for i, explanation in enumerate(explanations):
            student_id = student_ids[i]
            node_idx = explanation['node_idx']
            
            # 获取关键子图
            key_subgraph = self.get_key_subgraph(data, explanation)
            
            # 分析特征重要性
            feat_importance = explanation['node_feat_mask']
            top_features = np.argsort(feat_importance)[-5:][::-1]
            
            # 生成报告
            student_report = {
                'student_id': student_id,
                'node_idx': node_idx,
                'key_nodes': key_subgraph['nodes'],
                'key_edges': key_subgraph['edges'],
                'top_features': top_features.tolist(),
                'feature_importance': feat_importance.tolist(),
                'edge_importance': explanation['edge_mask'].tolist()
            }
            
            report.append(student_report)
        
        return report

class ExplanationEvaluator:
    """解释评估器"""
    
    def __init__(self):
        self.metrics = {}
    
    def compute_faithfulness(self, model, data, explanation, node_idx):
        """计算忠实度指标"""
        # 获取原始预测
        original_pred = model(data).argmax(dim=1)[node_idx].item()
        
        # 使用解释掩码修改图结构
        edge_mask = explanation['edge_mask']
        important_edges = edge_mask > 0.5
        
        # 创建修改后的图
        modified_edge_index = data.edge_index[:, important_edges]
        
        if modified_edge_index.shape[1] == 0:
            return 0.0
        
        modified_data = data.clone()
        modified_data.edge_index = modified_edge_index
        
        # 获取修改后的预测
        modified_pred = model(modified_data).argmax(dim=1)[node_idx].item()
        
        # 忠实度：修改后的预测与原始预测一致的程度
        faithfulness = 1.0 if modified_pred == original_pred else 0.0
        
        return faithfulness
    
    def compute_stability(self, model, data, node_idx, num_runs=5):
        """计算稳定性指标"""
        explanations = []
        
        for _ in range(num_runs):
            explainer = GNNExplainer(model, epochs=100, lr=0.01)
            node_feat_mask, edge_mask = explainer.explain_node(node_idx, data.x, data.edge_index)
            explanations.append({
                'node_feat_mask': node_feat_mask.detach().cpu().numpy(),
                'edge_mask': edge_mask.detach().cpu().numpy()
            })
        
        # 计算不同运行之间的相似度
        similarities = []
        for i in range(len(explanations)):
            for j in range(i + 1, len(explanations)):
                # 计算边掩码的余弦相似度
                mask1 = explanations[i]['edge_mask']
                mask2 = explanations[j]['edge_mask']
                
                if len(mask1) > 0 and len(mask2) > 0:
                    # 确保长度相同
                    min_len = min(len(mask1), len(mask2))
                    mask1 = mask1[:min_len]
                    mask2 = mask2[:min_len]
                    
                    similarity = np.dot(mask1, mask2) / (np.linalg.norm(mask1) * np.linalg.norm(mask2))
                    similarities.append(similarity)
        
        stability = np.mean(similarities) if similarities else 0.0
        
        return stability
    
    def compute_completeness(self, model, data, explanation, node_idx):
        """计算完整性指标"""
        # 获取原始预测
        original_pred = model(data).argmax(dim=1)[node_idx].item()
        
        # 使用解释掩码的补集修改图结构
        edge_mask = explanation['edge_mask']
        unimportant_edges = edge_mask <= 0.5
        
        if unimportant_edges.sum() == 0:
            return 1.0
        
        modified_edge_index = data.edge_index[:, unimportant_edges]
        
        if modified_edge_index.shape[1] == 0:
            return 1.0
        
        modified_data = data.clone()
        modified_data.edge_index = modified_edge_index
        
        # 获取修改后的预测
        modified_pred = model(modified_data).argmax(dim=1)[node_idx].item()
        
        # 完整性：移除不重要边后预测改变的程度
        completeness = 1.0 if modified_pred != original_pred else 0.0
        
        return completeness
    
    def evaluate_all_metrics(self, model, data, explanations, student_ids):
        """评估所有指标"""
        all_metrics = []
        
        for i, explanation in enumerate(explanations):
            student_id = student_ids[i]
            node_idx = explanation['node_idx']
            
            metrics = {
                'student_id': student_id,
                'node_idx': node_idx,
                'faithfulness': self.compute_faithfulness(model, data, explanation, node_idx),
                'stability': self.compute_stability(model, data, node_idx),
                'completeness': self.compute_completeness(model, data, explanation, node_idx)
            }
            
            all_metrics.append(metrics)
        
        # 计算平均指标
        avg_metrics = {
            'avg_faithfulness': np.mean([m['faithfulness'] for m in all_metrics]),
            'avg_stability': np.mean([m['stability'] for m in all_metrics]),
            'avg_completeness': np.mean([m['completeness'] for m in all_metrics])
        }
        
        return all_metrics, avg_metrics

def save_explanation_results(explanations, filename='gnn_explanations.json'):
    """保存解释结果"""
    import json
    
    # 将numpy数组转换为列表以便JSON序列化
    serializable_explanations = []
    for exp in explanations:
        serializable_exp = {
            'student_id': exp['student_id'],
            'node_idx': exp['node_idx'],
            'key_nodes': exp['key_nodes'],
            'key_edges': exp['key_edges'],
            'top_features': exp['top_features'],
            'feature_importance': exp['feature_importance'],
            'edge_importance': exp['edge_importance']
        }
        serializable_explanations.append(serializable_exp)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(serializable_explanations, f, ensure_ascii=False, indent=2)

def load_explanation_results(filename='gnn_explanations.json'):
    """加载解释结果"""
    import json
    
    with open(filename, 'r', encoding='utf-8') as f:
        explanations = json.load(f)
    
    return explanations