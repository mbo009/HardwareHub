export type Row = {
  id?: number;
  name: string;
  brand: string;
  serial: string;
  date: string;
  status: "Available" | "Rented" | "In Repair" | "Unknown";
  category?: string;
};

export type HardwareCreateResponse = {
  id: number;
  name: string;
  brand: string;
  purchaseDate: string | null;
  status: "Available" | "In Use" | "Repair" | "Unknown";
};

export type HardwareRepairResponse = {
  id: number;
  status: "Available" | "In Use" | "Repair" | "Unknown";
  assignedTo: string | null;
  wasInUse: boolean;
};

export type HardwareListItem = {
  id: number;
  seedId: number | null;
  name: string;
  brand: string;
  purchaseDate: string | null;
  status: "Available" | "In Use" | "Repair" | "Unknown";
  notes: string | null;
};

export type HardwareListResponse = {
  items: HardwareListItem[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
};
