export const HARDWARE_INVENTORY_CHANGED_EVENT = "hardwarehub:hardware-inventory-changed";

export function emitHardwareInventoryChanged(): void {
  window.dispatchEvent(new CustomEvent(HARDWARE_INVENTORY_CHANGED_EVENT));
}
