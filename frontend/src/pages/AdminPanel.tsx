import React, { useCallback, useEffect, useMemo, useState } from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Typography from "@mui/joy/Typography";
import { apiFetch, type ApiError } from "../api/client";
import AppShell from "../components/AppShell";
import AddDeviceModal from "../components/admin/AddDeviceModal";
import AdminDevicesTable from "../components/admin/AdminDevicesTable";
import AdminFilters from "../components/admin/AdminFilters";
import ConfirmDeleteModal from "../components/admin/ConfirmDeleteModal";
import ConfirmReturnModal from "../components/admin/ConfirmReturnModal";
import CreateUserModal from "../components/admin/CreateUserModal";
import EditDeviceModal from "../components/admin/EditDeviceModal";
import type {
  AdminUserCreateResponse,
  HardwareCreateResponse,
  HardwareListItem,
  HardwareListResponse,
  HardwareRepairResponse,
  HardwareUpdateResponse,
  Row,
} from "../components/admin/types";
import { HARDWARE_INVENTORY_CHANGED_EVENT } from "../hardware/inventoryEvents";
import { buildHardwareListSearchParams } from "../hardware/hardwareListQuery";

export default function AdminPanelPage() {
  const [rows, setRows] = useState<Row[]>([]);
  const [isLoadingRows, setIsLoadingRows] = useState(true);
  const [loadRowsError, setLoadRowsError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [brandFilter, setBrandFilter] = useState("");
  const [debouncedBrandFilter, setDebouncedBrandFilter] = useState("");
  const [dateFromFilter, setDateFromFilter] = useState("");
  const [dateToFilter, setDateToFilter] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "brand" | "serial" | "purchaseDate" | "status">("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [serial, setSerial] = useState("");
  const [brand, setBrand] = useState("");
  const [notes, setNotes] = useState("");
  const [category, setCategory] = useState<string | null>(null);
  const [onSiteDate, setOnSiteDate] = useState("");
  const [touched, setTouched] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [deletingSerial, setDeletingSerial] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [repairError, setRepairError] = useState<string | null>(null);
  const [repairingSerial, setRepairingSerial] = useState<string | null>(null);
  const [repairNotice, setRepairNotice] = useState<string | null>(null);
  const [pendingDeleteRow, setPendingDeleteRow] = useState<Row | null>(null);
  const [pendingRepairRow, setPendingRepairRow] = useState<Row | null>(null);
  const [pendingEditRow, setPendingEditRow] = useState<Row | null>(null);
  const [editName, setEditName] = useState("");
  const [editBrand, setEditBrand] = useState("");
  const [editSerial, setEditSerial] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [editAssignedTo, setEditAssignedTo] = useState("");
  const [editStatus, setEditStatus] = useState<Row["status"]>("Available");
  const [isEditSubmitting, setIsEditSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [openCreateUser, setOpenCreateUser] = useState(false);
  const [createUserEmail, setCreateUserEmail] = useState("");
  const [createUserAsAdmin, setCreateUserAsAdmin] = useState(false);
  const [createUserSubmitting, setCreateUserSubmitting] = useState(false);
  const [createUserError, setCreateUserError] = useState<string | null>(null);
  const [generatedTempPassword, setGeneratedTempPassword] = useState<
    string | null
  >(null);

  const existingSerials = useMemo(
    () => new Set(rows.map((row) => row.serial.toLowerCase())),
    [rows],
  );

  const trimmedName = name.trim();
  const trimmedSerial = serial.trim();
  const trimmedBrand = brand.trim();
  const trimmedNotes = notes.trim();

  const serialTaken =
    trimmedSerial.length > 0 &&
    existingSerials.has(trimmedSerial.toLowerCase());
  const isValid =
    trimmedName.length > 0 &&
    trimmedBrand.length > 0 &&
    Boolean(category) &&
    !serialTaken;

  const resetForm = () => {
    setName("");
    setSerial("");
    setBrand("");
    setNotes("");
    setCategory(null);
    setOnSiteDate("");
    setTouched(false);
    setSubmitError(null);
  };

  const closeModal = () => {
    setOpen(false);
    resetForm();
  };

  const toUiStatus = (status: HardwareCreateResponse["status"]): Row["status"] => {
    if (status === "In Use") return "Rented";
    if (status === "Repair") return "In Repair";
    if (status === "Unknown") return "Unknown";
    return "Available";
  };

  useEffect(() => {
    const t = window.setTimeout(() => {
      setDebouncedBrandFilter(brandFilter.trim());
      setPage(1);
    }, 400);
    return () => {
      window.clearTimeout(t);
    };
  }, [brandFilter]);

  const loadRows = useCallback(
    (forcedPage?: number) => {
      setIsLoadingRows(true);
      setLoadRowsError(null);
      const effectivePage = forcedPage !== undefined ? forcedPage : page;
      const params = buildHardwareListSearchParams({
        statusFilter,
        brandFilter: debouncedBrandFilter,
        dateFrom: dateFromFilter,
        dateTo: dateToFilter,
        sortBy,
        sortOrder,
        page: effectivePage,
        limit: 8,
      });
      const path = `/api/hardware?${params.toString()}`;

      apiFetch<HardwareListResponse>(path)
        .then((response) => {
          const mapped: Row[] = response.items.map((item) => ({
            id: item.id,
            name: item.name,
            brand: item.brand,
            serial: item.serialNumber || "",
            date: item.purchaseDate || "-",
            preArrival: Boolean(item.preArrival),
            status: toUiStatus(item.status),
            assignedTo: item.assignedTo,
            notes: item.notes,
          }));
          setRows(mapped);
          const tp = Math.max(1, response.totalPages || 1);
          setTotalPages(tp);
          if (forcedPage !== undefined) {
            setPage(Math.min(forcedPage, tp));
          }
        })
        .catch(() => {
          setLoadRowsError("Could not load hardware list.");
        })
        .finally(() => {
          setIsLoadingRows(false);
        });
    },
    [dateFromFilter, dateToFilter, debouncedBrandFilter, page, sortBy, sortOrder, statusFilter],
  );

  useEffect(() => {
    loadRows();
  }, [loadRows]);

  useEffect(() => {
    const onInventoryChanged = () => {
      void loadRows(1);
    };
    window.addEventListener(HARDWARE_INVENTORY_CHANGED_EVENT, onInventoryChanged);
    return () =>
      window.removeEventListener(HARDWARE_INVENTORY_CHANGED_EVENT, onInventoryChanged);
  }, [loadRows]);

  const addDevice = async () => {
    setTouched(true);
    setSubmitError(null);
    if (!isValid) {
      return;
    }

    setIsSubmitting(true);
    try {
      const purchaseDate =
        onSiteDate.trim() !== ""
          ? onSiteDate.trim()
          : new Date().toISOString().slice(0, 10);
      const created = await apiFetch<HardwareCreateResponse>("/api/admin/hardware", {
        method: "POST",
        body: JSON.stringify({
          name: trimmedName,
          brand: trimmedBrand,
          serialNumber: trimmedSerial || null,
          status: "Available",
          purchaseDate,
          notes: trimmedNotes || null,
          history: `Category: ${category || "Other"}`,
        }),
      });

      setRows((prev) => [
        {
          id: created.id,
          name: created.name,
          brand: created.brand,
          serial: created.serialNumber || "",
          date: created.purchaseDate || new Date().toISOString().slice(0, 10),
          preArrival: Boolean(created.preArrival),
          status: toUiStatus(created.status),
          notes: created.notes,
          category: category || "Other",
        },
        ...prev,
      ]);
      closeModal();
      loadRows();
    } catch (error) {
      const err = error as ApiError;
      if (err?.status === 401) {
        setSubmitError("Session expired. Please log in again.");
      } else if (err?.status === 403) {
        setSubmitError("Only admins can add devices.");
      } else if (err?.status === 400) {
        const code =
          err?.data && typeof err.data === "object" && err.data !== null
            ? (err.data as { error?: string }).error
            : undefined;
        if (code === "invalid_purchase_date") {
          setSubmitError("Invalid on-site date. Use YYYY-MM-DD.");
        } else {
          setSubmitError("Could not add device. Check the form and try again.");
        }
      } else {
        setSubmitError("Could not add device. Try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const removeDevice = async (row: Row) => {
    setDeleteError(null);
    setDeletingSerial(row.serial);
    try {
      if (row.id) {
        await apiFetch<{ ok: boolean }>(`/api/admin/hardware/${row.id}`, {
          method: "DELETE",
        });
      }
      loadRows();
    } catch (error) {
      const err = error as ApiError;
      const errorCode =
        err?.data && typeof err.data === "object" && "error" in err.data
          ? String((err.data as { error?: string }).error || "")
          : "";

      if (err?.status === 409 && errorCode === "hardware_in_use") {
        setDeleteError("You cannot delete a rented device. Return it first.");
      } else if (err?.status === 404 && errorCode === "hardware_not_found") {
        setDeleteError("This device no longer exists. Refresh the list.");
      } else if (err?.status === 401) {
        setDeleteError("Session expired. Please log in again.");
      } else if (err?.status === 403) {
        setDeleteError("Only admins can delete devices.");
      } else {
        setDeleteError("Could not delete device. Try again.");
      }
    } finally {
      setDeletingSerial(null);
    }
  };

  const markInRepair = async (row: Row) => {
    setRepairError(null);
    setRepairNotice(null);

    setRepairingSerial(row.serial);
    try {
      if (!row.id) {
        setRepairError("Could not update status for this device.");
        return;
      }

      const response = await apiFetch<HardwareRepairResponse>(
        `/api/admin/hardware/${row.id}/repair`,
        {
          method: "PATCH",
        },
      );

      if (response.wasInUse) {
        setRepairNotice("Device was returned and status changed to available.");
      } else if (response.status === "Available") {
        setRepairNotice("Device status changed to available.");
      } else {
        setRepairNotice("Device status changed to in repair.");
      }
      loadRows();
    } catch (error) {
      const err = error as ApiError;
      const errorCode =
        err?.data && typeof err.data === "object" && "error" in err.data
          ? String((err.data as { error?: string }).error || "")
          : "";

      if (err?.status === 404 && errorCode === "hardware_not_found") {
        setRepairError("This device no longer exists. Refresh the list.");
      } else if (err?.status === 401) {
        setRepairError("Session expired. Please log in again.");
      } else if (err?.status === 403) {
        setRepairError("Only admins can update device status.");
      } else {
        setRepairError("Could not set device to in repair. Try again.");
      }
    } finally {
      setRepairingSerial(null);
    }
  };

  const closeDeleteModal = () => {
    if (deletingSerial) {
      return;
    }
    setPendingDeleteRow(null);
  };

  const closeRepairModal = () => {
    if (repairingSerial) {
      return;
    }
    setPendingRepairRow(null);
  };

  const closeEditModal = () => {
    if (isEditSubmitting) {
      return;
    }
    setPendingEditRow(null);
    setEditError(null);
  };

  const closeCreateUserModal = () => {
    if (createUserSubmitting) {
      return;
    }
    setOpenCreateUser(false);
    setCreateUserEmail("");
    setCreateUserAsAdmin(false);
    setCreateUserError(null);
    setGeneratedTempPassword(null);
  };

  const createUser = async () => {
    const email = createUserEmail.trim().toLowerCase();
    if (!email) {
      setCreateUserError("Email is required.");
      return;
    }
    if (!email.endsWith("@booksy.com")) {
      setCreateUserError("Email must use @booksy.com domain.");
      return;
    }

    setCreateUserSubmitting(true);
    setCreateUserError(null);
    try {
      const response = await apiFetch<AdminUserCreateResponse>("/api/admin/users", {
        method: "POST",
        body: JSON.stringify({
          email,
          role: createUserAsAdmin ? "admin" : "user",
        }),
      });
      setGeneratedTempPassword(response.temporaryPassword);
    } catch (error) {
      const err = error as ApiError;
      const errorCode =
        err?.data && typeof err.data === "object" && "error" in err.data
          ? String((err.data as { error?: string }).error || "")
          : "";

      if (err?.status === 409 && errorCode === "email_already_exists") {
        setCreateUserError("User with this email already exists.");
      } else if (err?.status === 400 && errorCode === "invalid_email") {
        setCreateUserError("Enter a valid email address.");
      } else if (err?.status === 400 && errorCode === "invalid_email_domain") {
        setCreateUserError("Email must use @booksy.com domain.");
      } else if (err?.status === 400 && errorCode === "invalid_role") {
        setCreateUserError("Invalid role.");
      } else if (err?.status === 400 && errorCode === "invalid_password") {
        setCreateUserError(
          "Server expected a password. Restart the backend so user creation uses temporary passwords.",
        );
      } else if (err?.status === 401) {
        setCreateUserError("Session expired. Please log in again.");
      } else if (err?.status === 403) {
        setCreateUserError("Only admins can create users.");
      } else {
        setCreateUserError("Could not create user. Try again.");
      }
    } finally {
      setCreateUserSubmitting(false);
    }
  };

  const openEditModal = (row: Row) => {
    setEditError(null);
    setPendingEditRow(row);
    setEditName(row.name);
    setEditBrand(row.brand);
    setEditSerial(row.serial);
    setEditNotes(row.notes || "");
    setEditAssignedTo(row.assignedTo || "");
    setEditStatus(row.status);
  };

  const saveDeviceChanges = async () => {
    if (!pendingEditRow?.id) {
      return;
    }

    const trimmedEditName = editName.trim();
    const trimmedEditBrand = editBrand.trim();
    const trimmedEditSerial = editSerial.trim();
    const trimmedEditNotes = editNotes.trim();
    const normalizedEmail = editAssignedTo.trim().toLowerCase();

    if (!trimmedEditName || !trimmedEditBrand) {
      setEditError("Name and brand are required.");
      return;
    }

    if (editStatus === "Rented" && !normalizedEmail) {
      setEditError("Provide user email to set status to rented.");
      return;
    }

    const apiStatus =
      normalizedEmail
        ? "In Use"
        : editStatus === "Rented"
          ? "In Use"
          : editStatus === "In Repair"
            ? "Repair"
            : editStatus;

    setIsEditSubmitting(true);
    setEditError(null);
    try {
      await apiFetch<HardwareUpdateResponse>(
        `/api/admin/hardware/${pendingEditRow.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            name: trimmedEditName,
            brand: trimmedEditBrand,
            serialNumber: trimmedEditSerial || null,
            notes: trimmedEditNotes || null,
            status: apiStatus,
            assignedTo: normalizedEmail || null,
          }),
        },
      );
      closeEditModal();
      loadRows();
    } catch (error) {
      const err = error as ApiError;
      const errorCode =
        err?.data && typeof err.data === "object" && "error" in err.data
          ? String((err.data as { error?: string }).error || "")
          : "";

      if (err?.status === 400 && errorCode === "assigned_user_not_found") {
        setEditError("Assigned user does not exist.");
      } else if (
        err?.status === 400 && errorCode === "assigned_to_required_for_in_use"
      ) {
        setEditError("Assigned email is required for rented status.");
      } else if (err?.status === 401) {
        setEditError("Session expired. Please log in again.");
      } else if (err?.status === 403) {
        setEditError("Only admins can edit devices.");
      } else {
        setEditError("Could not update device. Try again.");
      }
    } finally {
      setIsEditSubmitting(false);
    }
  };

  return (
    <AppShell title="Hardware Management">
      <Box
        sx={{
          display: "flex",
          justifyContent: "flex-end",
          gap: 0.8,
          mb: 0.7,
          width: "100%",
          maxWidth: 790,
        }}
      >
        <Button
          size="sm"
          variant="outlined"
          color="neutral"
          onClick={() => {
            setCreateUserAsAdmin(false);
            setOpenCreateUser(true);
          }}
          sx={{
            minHeight: 24,
            fontSize: 9.6,
            px: 1.2,
            borderRadius: "sm",
          }}
        >
          Create User
        </Button>
        <Button
          size="sm"
          onClick={() => setOpen(true)}
          sx={{
            bgcolor: "#0b1220",
            ":hover": { bgcolor: "#0b1220" },
            minHeight: 24,
            fontSize: 9.6,
            px: 1.2,
            borderRadius: "sm",
          }}
        >
          Add New Device
        </Button>
      </Box>

      <AdminFilters
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        brandFilter={brandFilter}
        setBrandFilter={setBrandFilter}
        dateFromFilter={dateFromFilter}
        setDateFromFilter={setDateFromFilter}
        dateToFilter={dateToFilter}
        setDateToFilter={setDateToFilter}
        onFilterChangeResetPage={() => setPage(1)}
        onReset={() => {
          setStatusFilter("");
          setBrandFilter("");
          setDebouncedBrandFilter("");
          setDateFromFilter("");
          setDateToFilter("");
          setPage(1);
        }}
      />

      <AddDeviceModal
        open={open}
        onClose={closeModal}
        name={name}
        setName={setName}
        serial={serial}
        setSerial={setSerial}
        brand={brand}
        setBrand={setBrand}
        notes={notes}
        setNotes={setNotes}
        category={category}
        setCategory={setCategory}
        onSiteDate={onSiteDate}
        setOnSiteDate={setOnSiteDate}
        touched={touched}
        serialTaken={serialTaken}
        isSubmitting={isSubmitting}
        submitError={submitError}
        onSubmit={addDevice}
      />

      <ConfirmDeleteModal
        open={Boolean(pendingDeleteRow)}
        row={pendingDeleteRow}
        isLoading={Boolean(deletingSerial)}
        onCancel={closeDeleteModal}
        onConfirm={() => {
          if (!pendingDeleteRow) return;
          void removeDevice(pendingDeleteRow).finally(() => {
            setPendingDeleteRow(null);
          });
        }}
      />

      <CreateUserModal
        open={openCreateUser}
        email={createUserEmail}
        setEmail={setCreateUserEmail}
        adminPrivileges={createUserAsAdmin}
        setAdminPrivileges={setCreateUserAsAdmin}
        isSubmitting={createUserSubmitting}
        submitError={createUserError}
        generatedPassword={generatedTempPassword}
        onClose={closeCreateUserModal}
        onSubmit={() => {
          void createUser();
        }}
      />

      <ConfirmReturnModal
        open={Boolean(pendingRepairRow)}
        isLoading={Boolean(repairingSerial)}
        onCancel={closeRepairModal}
        onConfirm={() => {
          if (!pendingRepairRow) return;
          void markInRepair(pendingRepairRow).finally(() => {
            setPendingRepairRow(null);
          });
        }}
      />

      <EditDeviceModal
        open={Boolean(pendingEditRow)}
        row={pendingEditRow}
        name={editName}
        setName={setEditName}
        brand={editBrand}
        setBrand={setEditBrand}
        serial={editSerial}
        setSerial={setEditSerial}
        notes={editNotes}
        setNotes={setEditNotes}
        assignedTo={editAssignedTo}
        setAssignedTo={setEditAssignedTo}
        status={editStatus}
        setStatus={setEditStatus}
        isSubmitting={isEditSubmitting}
        submitError={editError}
        onClose={closeEditModal}
        onSubmit={() => {
          void saveDeviceChanges();
        }}
      />

      <AdminDevicesTable
        rows={rows}
        isLoadingRows={isLoadingRows}
        loadRowsError={loadRowsError}
        deleteError={deleteError}
        repairError={repairError}
        repairNotice={repairNotice}
        deletingSerial={deletingSerial}
        repairingSerial={repairingSerial}
        onRequestDelete={(row) => {
          setDeleteError(null);
          setPendingDeleteRow(row);
        }}
        onRequestEdit={openEditModal}
        onRequestReturn={setPendingRepairRow}
        onRepair={(row) => {
          void markInRepair(row);
        }}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSort={(field) => {
          setPage(1);
          if (sortBy === field) {
            setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
            return;
          }
          setSortBy(field);
          setSortOrder("asc");
        }}
      />
      <Box sx={{ width: "100%", maxWidth: 790, mt: 0.7, display: "flex", justifyContent: "flex-end", gap: 0.8 }}>
        <Button
          size="sm"
          variant="outlined"
          color="neutral"
          disabled={page <= 1 || isLoadingRows}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          Prev
        </Button>
        <Typography level="body-sm" sx={{ alignSelf: "center", color: "#6b7280" }}>
          Page {page} of {Math.max(1, totalPages)}
        </Typography>
        <Button
          size="sm"
          variant="outlined"
          color="neutral"
          disabled={page >= totalPages || isLoadingRows}
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
        >
          Next
        </Button>
      </Box>
    </AppShell>
  );
}

