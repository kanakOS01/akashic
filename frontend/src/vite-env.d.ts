/// <reference types="vite/client" />

declare module "virtual:akashic-snapshot" {
  const snapshot: import("./src/lib/types").Snapshot | null;
  export default snapshot;
}
