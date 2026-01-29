import { useAtom } from 'jotai';
import { agentsAtom, myAgentsAtom } from '../../store/atoms';
import { Search, Flame, Briefcase, Palette, BarChart2, Heart, Star, Check } from 'lucide-react';
import { useState } from 'react';
import './store.css';

export default function Store() {
  const [agents] = useAtom(agentsAtom);
  const [myAgents, setMyAgents] = useAtom(myAgentsAtom);
  const [search, setSearch] = useState('');

  // 过滤智能体
  const filteredAgents = agents.filter(
    (agent) =>
      search === '' ||
      agent.name.toLowerCase().includes(search.toLowerCase()) ||
      agent.description.toLowerCase().includes(search.toLowerCase())
  );

  // 获取智能体图标
  const getAgentIcon = (iconName) => {
    switch (iconName) {
      case '💰':
        return Briefcase;
      case '✍️':
        return Palette;
      case '📊':
        return BarChart2;
      case '💚':
        return Heart;
      default:
        return Briefcase;
    }
  };

  // 获取图标背景色
  const getIconBgColor = (iconName) => {
    switch (iconName) {
      case '💰':
        return '#FEF3C7';
      case '✍️':
        return '#FCE7F3';
      case '📊':
        return '#DBEAFE';
      case '💚':
        return '#D1FAE5';
      default:
        return '#E5E7EB';
    }
  };

  // 安装/卸载智能体
  const toggleAgent = (agentId) => {
    if (myAgents.includes(agentId)) {
      setMyAgents(myAgents.filter((id) => id !== agentId));
    } else {
      setMyAgents([...myAgents, agentId]);
    }
  };

  return (
    <div className="store-layout">
      <div className="store-content-wrapper">
        {/* 头部 */}
        <div className="store-header">
          <h1>智能体商店</h1>
          <button className="btn btn-primary">我的智能体</button>
        </div>

        {/* 搜索栏 */}
        <div className="store-search-section">
          <div className="store-search-bar">
            <div className="search-input-wrapper">
              <Search className="search-icon" />
              <input
                type="text"
                className="store-search-input"
                placeholder="搜索智能体..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="store-tags">
              <span className="tag tag-hot">
                <Flame style={{ width: '14px', height: '14px' }} />
                热门
              </span>
              <span className="tag tag-work">
                <Briefcase style={{ width: '14px', height: '14px' }} />
                工作
              </span>
            </div>
          </div>
        </div>

        {/* 热门推荐 */}
        <h2 className="section-title">热门推荐</h2>
        <div className="agent-grid">
          {filteredAgents.map((agent) => {
            const Icon = getAgentIcon(agent.icon);
            const isInstalled = myAgents.includes(agent.id);

            return (
              <div
                key={agent.id}
                className={`agent-card ${isInstalled ? 'my-agent-card' : ''}`}
                onClick={() => !isInstalled && toggleAgent(agent.id)}
              >
                <div
                  className="agent-card-icon"
                  style={{ backgroundColor: getIconBgColor(agent.icon) }}
                >
                  <Icon style={{ width: '28px', height: '28px' }} />
                </div>
                {isInstalled ? (
                  <div className="my-agent-header">
                    <h3 className="agent-card-title">{agent.name}</h3>
                    <span className="my-agent-badge">
                      <Check style={{ width: '10px', height: '10px' }} />
                      已激活
                    </span>
                  </div>
                ) : (
                  <h3 className="agent-card-title">{agent.name}</h3>
                )}
                <p className="agent-card-description">{agent.description}</p>
                <p className="agent-card-rating">
                  <Star style={{ width: '14px', height: '14px', fill: 'currentColor' }} />
                  {agent.rating}
                </p>
                {isInstalled && (
                  <p className="my-agent-stats">
                    调用次数: 127次 | 最后使用: 2小时前
                  </p>
                )}
                <button
                  className={`agent-card-btn ${isInstalled ? 'installed' : ''}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleAgent(agent.id);
                  }}
                >
                  {isInstalled ? '已安装' : '安装'}
                </button>
              </div>
            );
          })}
        </div>

        {/* 我的智能体 */}
        {myAgents.length > 0 && (
          <>
            <h2 className="section-title">我的智能体 (已激活)</h2>
            <div className="agent-grid">
              {agents
                .filter((agent) => myAgents.includes(agent.id))
                .map((agent) => {
                  const Icon = getAgentIcon(agent.icon);
                  return (
                    <div key={agent.id} className="agent-card my-agent-card">
                      <div
                        className="agent-card-icon"
                        style={{ backgroundColor: getIconBgColor(agent.icon) }}
                      >
                        <Icon style={{ width: '28px', height: '28px' }} />
                      </div>
                      <div className="my-agent-header">
                        <h3 className="agent-card-title">{agent.name}</h3>
                        <span className="my-agent-badge">
                          <Check style={{ width: '10px', height: '10px' }} />
                          已激活
                        </span>
                      </div>
                      <p className="agent-card-description">{agent.description}</p>
                      <p className="my-agent-stats">
                        调用次数: 127次 | 最后使用: 2小时前
                      </p>
                      <button className="agent-card-btn installed" onClick={(e) => e.stopPropagation()}>
                        已安装
                      </button>
                    </div>
                  );
                })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
