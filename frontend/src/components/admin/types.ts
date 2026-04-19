export type Row = {
  id?: number;
  name: string;
  brand: string;
  serial: string;
  date: string;
  status: "Available" | "Rented" | "In Repair" | "Unknown";
  preArrival?: boolean;
  notes?: string | null;
  assignedTo?: string | null;
  category?: string;
};

export type HardwareCreateResponse = {
  id: number;
  name: string;
  brand: string;
  serialNumber: string | null;
  purchaseDate: string | null;
  status: "Available" | "In Use" | "Repair" | "Unknown";
  notes: string | null;
  preArrival?: boolean;
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
  serialNumber: string | null;
  purchaseDate: string | null;
  status: "Available" | "In Use" | "Repair" | "Unknown";
  assignedTo: string | null;
  notes: string | null;
  preArrival?: boolean;
};

export type HardwareUpdateResponse = {
  id: number;
  name: string;
  brand: string;
  serialNumber: string | null;
  purchaseDate: string | null;
  status: "Available" | "In Use" | "Repair" | "Unknown";
  assignedTo: string | null;
  notes: string | null;
  preArrival?: boolean;
};

export type AdminUserCreateResponse = {
  id: number;
  email: string;
  role: "admin" | "user";
  temporaryPassword: string;
  mustChangePassword: boolean;
};

export type HardwareListResponse = {
  items: HardwareListItem[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
};
