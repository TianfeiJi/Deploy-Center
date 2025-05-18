import { boot } from 'quasar/wrappers';
import { useAgentStore } from 'src/stores/useAgentStore';
import { useAuthStore } from 'src/stores/useAuthStore';

export default boot(async () => {
  const authStore = useAuthStore();
  if (authStore.token) {
    const agentStore = useAgentStore();
    await agentStore.initAgentStore();
  }
});
