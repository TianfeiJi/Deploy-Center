import PythonProjectDetailDialog from 'src/components/project/dialogs/PythonProjectDetailDialog.vue'
import JavaProjectDetailDialog from 'src/components/project/dialogs/JavaProjectDetailDialog.vue'
import WebProjectDetailDialog from 'src/components/project/dialogs/WebProjectDetailDialog.vue'


export const projectDetailDialogMap = {
  python: PythonProjectDetailDialog,
  java: JavaProjectDetailDialog,
  web: WebProjectDetailDialog,
} as const