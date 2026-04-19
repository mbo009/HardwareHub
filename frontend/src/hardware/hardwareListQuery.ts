const STATUS_MAP: Record<string, string> = {
  Available: "Available",
  Ordered: "Ordered",
  Rented: "In Use",
  "In Repair": "Repair",
  Unknown: "Unknown",
};

export type HardwareListQueryOpts = {
  statusFilter: string;
  brandFilter: string;
  dateFrom: string;
  dateTo: string;
  sortBy: string;
  sortOrder: "asc" | "desc";
  page: number;
  limit: number;
  /** When set, restricts list to this assignee (must match session user for user routes). */
  assignedToEmail?: string;
};

export function buildHardwareListSearchParams(
  opts: HardwareListQueryOpts,
): URLSearchParams {
  const p = new URLSearchParams();
  const email = (opts.assignedToEmail || "").trim();
  if (email) {
    p.set("assignedTo", email.toLowerCase());
  }
  if (opts.statusFilter) {
    p.set("status", STATUS_MAP[opts.statusFilter] || opts.statusFilter);
  }
  if (opts.brandFilter.trim()) {
    p.set("brand", opts.brandFilter.trim());
  }
  if (opts.dateFrom) {
    p.set("dateFrom", opts.dateFrom);
  }
  if (opts.dateTo) {
    p.set("dateTo", opts.dateTo);
  }
  const sortByParam =
    opts.sortBy === "serial" ? "serialNumber" : opts.sortBy || "name";
  p.set("sortBy", sortByParam);
  p.set("order", opts.sortOrder);
  p.set("page", String(opts.page));
  p.set("limit", String(opts.limit));
  return p;
}
