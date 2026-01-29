import { useEffect, useState } from 'react';
import { useLocation } from 'react-router';

export function PageTransition({ children }) {
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const [transitionStage, setTransitionStage] = useState('fadeIn');

  useEffect(() => {
    if (location !== displayLocation) {
      setTransitionStage('fadeOut');
    }
  }, [location, displayLocation]);

  const handleTransitionEnd = () => {
    if (transitionStage === 'fadeOut') {
      setTransitionStage('fadeIn');
      setDisplayLocation(location);
      // 滚动到顶部
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div
      className={`page-transition-${transitionStage}`}
      onTransitionEnd={handleTransitionEnd}
      style={{
        transition: 'opacity 0.3s ease-in-out, transform 0.3s ease-in-out',
      }}
    >
      {children}
    </div>
  );
}
