import { useAtom } from 'jotai';
import { settingsAtom } from '../../store/atoms';
import { User, Bot, Shield, Palette, Check } from 'lucide-react';
import { useState } from 'react';
import './settings.css';

export default function Settings() {
  const [settings, setSettings] = useAtom(settingsAtom);
  const [theme, setTheme] = useState('system');
  const [fontSize, setFontSize] = useState('default');
  const [companionPosition, setCompanionPosition] = useState('left');
  const [privacyEnabled, setPrivacyEnabled] = useState([true, true]);

  const updateSetting = (key, value) => {
    setSettings({ ...settings, [key]: value });
  };

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    updateSetting('theme', newTheme);
  };

  const handleFontSizeChange = (newFontSize) => {
    setFontSize(newFontSize);
    updateSetting('fontSize', newFontSize);
  };

  const handleCompanionPositionChange = (position) => {
    setCompanionPosition(position);
    updateSetting('companionPosition', position);
  };

  const handlePrivacyToggle = (index) => {
    const newPrivacy = [...privacyEnabled];
    newPrivacy[index] = !newPrivacy[index];
    setPrivacyEnabled(newPrivacy);
  };

  const handleLogout = () => {
    alert('退出登录');
  };

  const handleDeleteAccount = () => {
    if (confirm('确定要删除账户吗？此操作不可恢复，所有数据将被永久删除。')) {
      if (confirm('再次确认：真的要删除账户吗？')) {
        alert('账户删除功能需要后端支持');
      }
    }
  };

  const handleClearMemories = () => {
    if (confirm('确定要清除所有记忆吗？此操作不可恢复。')) {
      alert('记忆清除功能需要后端支持');
    }
  };

  const handleExportData = () => {
    alert('导出数据功能需要后端支持');
  };

  return (
    <div className="settings-layout">
      <div className="settings-content-wrapper">
        <h1 className="settings-page-title">设置</h1>

        {/* 账户管理 */}
        <section className="settings-section">
          <h2 className="settings-section-title">
            <User style={{ width: '20px', height: '20px' }} />
            账户管理
          </h2>

          <div className="account-avatar-section">
            <div className="account-avatar">张</div>
            <div className="account-avatar-label">
              <p>头像</p>
              <a href="#">[更换]</a>
            </div>
          </div>

          <div className="account-field">
            <p className="account-field-label">昵称</p>
            <p className="account-field-value">张三</p>
          </div>

          <div className="account-field">
            <p className="account-field-label">邮箱</p>
            <p className="account-field-value">zhang***@email.com</p>
          </div>

          <div className="account-actions">
            <button className="btn btn-secondary" onClick={handleLogout}>
              退出登录
            </button>
            <button
              className="btn btn-danger"
              onClick={handleDeleteAccount}
            >
              删除账户
            </button>
          </div>
        </section>

        {/* LLM 模型配置 */}
        <section className="settings-section">
          <h2 className="settings-section-title">
            <Bot style={{ width: '20px', height: '20px' }} />
            LLM模型配置
          </h2>

          <div className="llm-field">
            <p className="llm-field-label">主模型</p>
            <p className="llm-field-value">
              <span>MiniMax</span>
              <a href="#">[切换]</a>
            </p>
          </div>

          <div className="llm-field">
            <p className="llm-field-label">温度值</p>
            <p className="llm-field-value">
              0.7
              <a href="#">[?]</a>
            </p>
          </div>

          <div className="llm-field">
            <p className="llm-field-label">APIKey</p>
            <p className="llm-field-value">
              ••••••••••••••••
              <a href="#">[修改]</a>
            </p>
          </div>
        </section>

        {/* 隐私与安全 */}
        <section className="settings-section">
          <h2 className="settings-section-title">
            <Shield style={{ width: '20px', height: '20px' }} />
            隐私与安全
          </h2>

          <div className="privacy-item" onClick={() => handlePrivacyToggle(0)}>
            <div className="privacy-checkbox">
              <Check style={{ width: '12px', height: '12px' }} />
            </div>
            <p className="privacy-text">本地优先处理敏感数据</p>
          </div>

          <div className="privacy-item" onClick={() => handlePrivacyToggle(1)}>
            <div className="privacy-checkbox">
              <Check style={{ width: '12px', height: '12px' }} />
            </div>
            <p className="privacy-text">端到端加密传输</p>
          </div>

          <div className="privacy-select">
            <p className="account-field-label">自动记忆保留</p>
            <p className="account-field-value">
              <span>30天</span>
              <a href="#">▼</a>
            </p>
          </div>

          <div className="privacy-actions">
            <button className="btn btn-primary" onClick={handleExportData}>
              导出所有数据
            </button>
            <button
              className="btn btn-danger"
              onClick={handleClearMemories}
            >
              清除所有记忆
            </button>
          </div>
        </section>

        {/* 外观设置 */}
        <section className="settings-section">
          <h2 className="settings-section-title">
            <Palette style={{ width: '20px', height: '20px' }} />
            外观设置
          </h2>

          <div className="appearance-field">
            <p className="appearance-field-label">主题</p>
            <div className="theme-options">
              <button
                className={`theme-option ${theme === 'system' ? 'active' : ''}`}
                onClick={() => handleThemeChange('system')}
              >
                跟随系统
              </button>
              <button
                className={`theme-option ${theme === 'light' ? 'active' : ''}`}
                onClick={() => handleThemeChange('light')}
              >
                浅色
              </button>
              <button
                className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
                onClick={() => handleThemeChange('dark')}
              >
                深色
              </button>
            </div>
          </div>

          <div className="appearance-field">
            <p className="appearance-field-label">字体大小</p>
            <div className="theme-options">
              <button
                className={`theme-option ${fontSize === 'default' ? 'active' : ''}`}
                onClick={() => handleFontSizeChange('default')}
              >
                默认
              </button>
              <button
                className={`theme-option ${fontSize === 'large' ? 'active' : ''}`}
                onClick={() => handleFontSizeChange('large')}
              >
                大
              </button>
              <button
                className={`theme-option ${fontSize === 'xlarge' ? 'active' : ''}`}
                onClick={() => handleFontSizeChange('xlarge')}
              >
                特大
              </button>
            </div>
          </div>

          <div className="appearance-field">
            <p className="appearance-field-label">伴侣位置</p>
            <div className="theme-options">
              <button
                className={`theme-option ${companionPosition === 'left' ? 'active' : ''}`}
                onClick={() => handleCompanionPositionChange('left')}
              >
                左侧
              </button>
              <button
                className={`theme-option ${companionPosition === 'right' ? 'active' : ''}`}
                onClick={() => handleCompanionPositionChange('right')}
              >
                右侧
              </button>
              <button
                className={`theme-option ${companionPosition === 'bottom' ? 'active' : ''}`}
                onClick={() => handleCompanionPositionChange('bottom')}
              >
                底部
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
