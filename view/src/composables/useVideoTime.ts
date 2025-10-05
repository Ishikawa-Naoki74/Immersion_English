import { ref } from 'vue';

export function useVideoTime() {
  const currentTime = ref(0);
  let timeInterval: NodeJS.Timeout | null = null;

  const startTimeTracking = () => {
    timeInterval = setInterval(() => {
      currentTime.value += 1;
    }, 1000);
  };

  const stopTimeTracking = () => {
    if (timeInterval) {
      clearInterval(timeInterval);
      timeInterval = null;
    }
  };

  const resetTime = () => {
    currentTime.value = 0;
  };

  return {
    currentTime,
    startTimeTracking,
    stopTimeTracking,
    resetTime
  };
} 