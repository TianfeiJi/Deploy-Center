import axios from 'axios';

export const submitFeedback = async (feedback: { email: string; phone: string; message: string }) => {
  const response = await axios.post('/api/feedback', feedback);
  return response.data;
};