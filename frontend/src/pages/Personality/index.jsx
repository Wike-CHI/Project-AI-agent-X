import { useAtom } from 'jotai';
import { personalityAtom } from '../../store/atoms';
import { useState } from 'react';
import './personality.css';

const parameters = [
  {
    key: 'empathy',
    label: '共情能力',
    description: '决定伴侣对你情绪的敏感度和回应方式',
  },
  {
    key: 'humor',
    label: '幽默程度',
    description: null,
  },
  {
    key: 'seriousness',
    label: '严谨程度',
    description: '回复的正式程度和逻辑性',
  },
  {
    key: 'proactive',
    label: '主动程度',
    description: '主动发起对话和建议的频率',
  },
];

export default function Personality() {
  const [personality, setPersonality] = useAtom(personalityAtom);
  const [saveStatus, setSaveStatus] = useState('idle'); // idle, saving, success

  const handleParameterChange = (key, value) => {
    setPersonality({ ...personality, [key]: parseInt(value) });
  };

  const handleSave = () => {
    setSaveStatus('saving');
    console.log('保存性格配置:', personality);

    // 模拟保存过程
    setTimeout(() => {
      setSaveStatus('success');
      setTimeout(() => {
        setSaveStatus('idle');
      }, 2000);
    }, 1000);
  };

  return (
    <div className="personality-layout">
      <div className="personality-content-wrapper">
        {/* 头部 */}
        <div className="personality-header">
          <h1>性格养成系统</h1>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={saveStatus === 'saving'}
          >
            {saveStatus === 'idle' && '保存配置'}
            {saveStatus === 'saving' && '保存中...'}
            {saveStatus === 'success' && '保存成功！'}
          </button>
        </div>

        {/* 头像预览 */}
        <div className="avatar-preview-section">
          <div className="avatar-preview">小艾</div>
          <p className="avatar-label">伴侣3D/2D形象</p>
          <p className="avatar-label">实时预览区域</p>
        </div>

        {/* 性格参数 */}
        <div className="personality-params">
          <h2 className="params-title">性格参数</h2>

          {parameters.map((param) => {
            const value = personality[param.key];

            return (
              <div key={param.key} className="param-item">
                <div className="param-header">
                  <span className="param-label">{param.label}</span>
                  <span className="param-value">设置为 {value}%</span>
                </div>
                {param.description && (
                  <p className="param-description">{param.description}</p>
                )}
                <div className="param-slider-container">
                  <input
                    type="range"
                    className="param-range"
                    min="0"
                    max="100"
                    value={value}
                    onChange={(e) => handleParameterChange(param.key, e.target.value)}
                    style={{
                      background: `linear-gradient(to right, #7C3AED 0%, #7C3AED ${value}%, #EDE9FE ${value}%, #EDE9FE 100%)`,
                    }}
                  />
                  <div className="param-scale">
                    <span>低</span>
                    <span>高</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
