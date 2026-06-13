// cytoscape-fcose ships no types; we only need the registrable extension.
declare module "cytoscape-fcose" {
  import type { Ext } from "cytoscape";
  const ext: Ext;
  export default ext;
}
