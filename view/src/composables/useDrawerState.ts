import { ref } from 'vue';

export function  useDrawerState(){
  const leftDrawerOpen = ref(false);

  const toggleLeftDrawer = () => {
    leftDrawerOpen.value = !leftDrawerOpen.value;
  };
  
  return {
    leftDrawerOpen,
    toggleLeftDrawer,
  }
 }
