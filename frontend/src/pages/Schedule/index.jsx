import { useState } from 'react';
import { Plus, Clock, MapPin, AlertTriangle, Lightbulb, Sparkles } from 'lucide-react';
import './schedule.css';

export default function Schedule() {
  const [currentDate, setCurrentDate] = useState(new Date(2024, 0, 29)); // 2024年1月29日

  // 生成日历
  const generateCalendar = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const days = [];

    // 上个月的最后几天
    const prevMonthDays = new Date(year, month, 0).getDate();
    for (let i = firstDay - 1; i >= 0; i--) {
      days.push({
        day: prevMonthDays - i,
        isCurrentMonth: false,
        isToday: false,
      });
    }

    // 当月的天数
    for (let i = 1; i <= daysInMonth; i++) {
      days.push({
        day: i,
        isCurrentMonth: true,
        isToday: i === 29,
      });
    }

    // 下个月的前几天
    const remainingDays = 42 - days.length;
    for (let i = 1; i <= remainingDays; i++) {
      days.push({
        day: i,
        isCurrentMonth: false,
        isToday: false,
      });
    }

    return days;
  };

  const calendarDays = generateCalendar();

  const handleDayClick = (day) => {
    // 这里可以添加切换日期的逻辑
    console.log('Clicked day:', day);
  };

  return (
    <div className="schedule-layout">
      <div className="schedule-content-wrapper">
        {/* 头部 */}
        <div className="schedule-header">
          <h1>日程管理</h1>
          <button className="btn btn-primary">
            <Plus style={{ width: '16px', height: '16px' }} />
            添加日程
          </button>
        </div>

        {/* 内容区域 */}
        <div className="schedule-content">
          {/* 日历 */}
          <div className="calendar-section">
            <h2 className="calendar-title">2024年1月</h2>
            <div className="calendar-grid">
              <div className="calendar-weekday">日</div>
              <div className="calendar-weekday">一</div>
              <div className="calendar-weekday">二</div>
              <div className="calendar-weekday">三</div>
              <div className="calendar-weekday">四</div>
              <div className="calendar-weekday">五</div>
              <div className="calendar-weekday">六</div>

              {calendarDays.map((day, index) => (
                <div
                  key={index}
                  className={`calendar-day ${day.isToday ? 'today' : ''} ${
                    day.isCurrentMonth ? '' : 'opacity-50'
                  }`}
                  onClick={() => handleDayClick(day.day)}
                >
                  {day.day}
                </div>
              ))}
            </div>
          </div>

          {/* 当日日程 */}
          <div className="daily-schedule">
            <h2 className="day-title">今日 - 1月29日 星期三</h2>

            {/* 普通日程 */}
            <div className="schedule-event">
              <div className="schedule-event-header">
                <span className="event-time">
                  <Clock style={{ width: '14px', height: '14px' }} />
                  09:00 - 10:30
                </span>
              </div>
              <h3 className="event-title">项目评审会议</h3>
              <p className="event-location">
                <MapPin style={{ width: '14px', height: '14px' }} />
                会议室A | 参与者: 张三、李四
              </p>
              <div className="event-actions">
                <button className="btn btn-sm btn-secondary">查看详情</button>
                <button className="btn btn-sm btn-secondary">编辑</button>
              </div>
            </div>

            {/* 警告日程 */}
            <div className="schedule-event warning">
              <div className="schedule-event-header">
                <span className="event-time">
                  <Clock style={{ width: '14px', height: '14px' }} />
                  10:45 - 11:45
                </span>
              </div>
              <h3 className="event-title">代码审查</h3>
              <div className="event-warning">
                <AlertTriangle style={{ width: '12px', height: '12px' }} />
                与前一个会议间隔仅15分钟
              </div>
              <p className="event-location">
                <MapPin style={{ width: '14px', height: '14px' }} />
                在线会议
              </p>
              <div className="event-actions">
                <button className="btn btn-sm btn-secondary">查看详情</button>
                <button className="btn btn-sm btn-secondary">编辑</button>
              </div>
            </div>

            {/* AI建议 */}
            <div className="suggestion-card">
              <div className="suggestion-header">
                <Lightbulb className="suggestion-icon" style={{ width: '18px', height: '18px' }} />
                <span className="suggestion-title">AI 建议</span>
              </div>
              <p className="suggestion-content">
                两个会议只隔15分钟，建议推迟半小时，这样可以留出更多时间准备和休息。
              </p>
              <div className="suggestion-actions">
                <button className="btn btn-sm btn-primary">采纳建议</button>
                <button className="btn btn-sm btn-secondary">忽略</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
