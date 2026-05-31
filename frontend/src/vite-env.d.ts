/// <reference types="vite/client" />
declare global {
  namespace JSX {
    interface IntrinsicElements {
      ambientLight: any;
      directionalLight: any;
      group: any;
    }
  }
}
