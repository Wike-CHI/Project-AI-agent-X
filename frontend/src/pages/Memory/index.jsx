import { useAtom } from 'jotai';
import { memoriesAtom } from '../../store/atoms';
import { useState } from 'react';
import { Calendar, Tag, Coffee, Briefcase } from 'lucide-react';
import './memory.css';

export default function Memory() {
  const [memories] = useAtom(memoriesAtom);
  const [search, setSearch] = useState('');
  const [selectedTypes, setSelectedTypes] = useState(['episodic', 'semantic']);

  // 记忆图标映射
  const getMemoryIcon = (type) => {
    switch (type) {
      case 'episodic':
        return Calendar;
      case 'semantic':
        return Coffee;
      default:
        return Briefcase;
    }
  };

  // 过滤记忆
  const filteredMemories = memories.filter(
    (memory) =>
      (selectedTypes.includes(memory.type) || selectedTypes.length === 0) &&
      (search === '' ||
        memory.title.toLowerCase().includes(search.toLowerCase()) ||
        memory.content.toLowerCase().includes(search.toLowerCase()))
  );

  // 切换类型选择
  const toggleType = (type) => {
    if (selectedTypes.includes(type)) {
      setSelectedTypes(selectedTypes.filter((t) => t !== type));
    } else {
      setSelectedTypes([...selectedTypes, type]);
    }
  };

  return (
    <div className="memory-layout">
      <div className="memory-content-wrapper">
        {/* 头部 */}
        <div className="memory-header">
          <h1>记忆管理中心</h1>
          <div className="memory-actions">
            <button className="btn btn-secondary">导入</button>
            <button className="btn btn-primary">导出</button>
          </div>
        </div>

        {/* 内容区域 */}
        <div className="memory-content">
          {/* 过滤面板 */}
          <div className="filter-panel">
            <h2 className="filter-title">筛选条件</h2>

            <div className="filter-group">
              <label className="filter-label">搜索</label>
              <input
                type="text"
                className="input-field"
                placeholder="关键词搜索..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #E5E5E5',
                  borderRadius: '8px',
                  fontSize: '15px',
                  fontFamily: 'inherit',
                  outline: 'none',
                  transition: 'all 0.2s',
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#7C3AED';
                  e.target.style.boxShadow = '0 0 0 3px rgba(124, 58, 237, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#E5E5E5';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>

            <div className="filter-group">
              <label className="filter-label">记忆类型</label>
              <div
                className="filter-option"
                onClick={() => toggleType('episodic')}
              >
                <div
                  className={`filter-checkbox ${
                    selectedTypes.includes('episodic') ? 'checked' : ''
                  }`}
                ></div>
                <span className="filter-option-text">情景记忆</span>
              </div>
              <div
                className="filter-option"
                onClick={() => toggleType('semantic')}
              >
                <div
                  className={`filter-checkbox ${
                    selectedTypes.includes('semantic') ? 'checked' : ''
                  }`}
                ></div>
                <span className="filter-option-text">语义记忆</span>
              </div>
            </div>
          </div>

          {/* 记忆列表 */}
          <div className="memory-list">
            {filteredMemories.map((memory) => {
              const Icon = getMemoryIcon(memory.type);
              return (
                <div
                  key={memory.id}
                  className="memory-card"
                  onClick={() => alert('查看记忆详情')}
                >
                  <div className="memory-card-icon">
                    <Icon style={{ width: '24px', height: '24px' }} />
                  </div>
                  <h3 className="memory-card-title">
                    {memory.type === 'episodic' ? '情景记忆' : '语义记忆'}
                  </h3>
                  <p className="memory-card-content">"{memory.content}"</p>
                  <div className="memory-card-meta">
                    <span className="memory-card-meta-item">
                      <Calendar style={{ width: '14px', height: '14px' }} />
                      {memory.date}
                    </span>
                    <span className="memory-card-meta-item">
                      <Tag style={{ width: '14px', height: '14px' }} />
                      {memory.tags[0]}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
