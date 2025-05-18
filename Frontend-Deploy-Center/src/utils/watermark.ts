// src/utils/watermark.ts
interface WatermarkOptions {
    text: string
    opacity?: number
    fontSize?: number
    rotate?: number
  }
  
  const WATERMARK_ID = 'text-watermark'
  
  export function createWatermark({
    text,
    opacity = 0.1,
    fontSize = 20,
    rotate = -45
  }: WatermarkOptions): void {
    if (!text) return
  
    const existing = document.getElementById(WATERMARK_ID)
    if (existing) return
  
    const container = document.createElement('div')
    container.id = WATERMARK_ID
    const shadowRoot = container.attachShadow({ mode: 'closed' })
  
    const svgStr = `
      <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
        <text x="20" y="100" font-size="${fontSize}" fill="rgba(0,0,0,${opacity})" transform="rotate(${rotate})">
          ${text}
        </text>
      </svg>
    `
    const encodedSvg = encodeURIComponent(svgStr)
  
    const style = document.createElement('style')
    style.textContent = `
      div {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
        background-repeat: repeat;
        background-image: url("data:image/svg+xml;charset=utf-8,${encodedSvg}");
      }
    `
  
    const innerDiv = document.createElement('div')
    shadowRoot.appendChild(style)
    shadowRoot.appendChild(innerDiv)
  
    document.body.appendChild(container)
  }
  
  export function observeWatermark(options: WatermarkOptions): void {
    if (!options.text) return
  
    const observer = new MutationObserver(() => {
      if (!document.getElementById(WATERMARK_ID)) {
        createWatermark(options)
      }
    })
  
    observer.observe(document.body, { childList: true, subtree: true })
    createWatermark(options)
  }
