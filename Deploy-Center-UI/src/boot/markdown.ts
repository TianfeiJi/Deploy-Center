// src/boot/markdown.ts
import { boot } from 'quasar/wrappers'
// @ts-ignore
import VMdPreview from '@kangc/v-md-editor/lib/preview'
// @ts-ignore
import githubTheme from '@kangc/v-md-editor/lib/theme/github'
import '@kangc/v-md-editor/lib/style/preview.css'
import '@kangc/v-md-editor/lib/theme/style/github.css'


VMdPreview.use(githubTheme)

export default boot(({ app }) => {
  app.use(VMdPreview)
})
