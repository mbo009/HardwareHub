import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Input from "@mui/joy/Input";
import Option from "@mui/joy/Option";
import Select from "@mui/joy/Select";
import Stack from "@mui/joy/Stack";

type Props = {
  statusFilter: string;
  setStatusFilter: (value: string) => void;
  brandFilter: string;
  setBrandFilter: (value: string) => void;
  dateFromFilter: string;
  setDateFromFilter: (value: string) => void;
  dateToFilter: string;
  setDateToFilter: (value: string) => void;
  onReset: () => void;
  onFilterChangeResetPage: () => void;
};

export default function AdminFilters(props: Props) {
  const {
    statusFilter,
    setStatusFilter,
    brandFilter,
    setBrandFilter,
    dateFromFilter,
    setDateFromFilter,
    dateToFilter,
    setDateToFilter,
    onReset,
    onFilterChangeResetPage,
  } = props;

  return (
    <Box sx={{ width: "100%", maxWidth: 790, mb: 0.7 }}>
      <Stack direction="row" spacing={0.6} sx={{ alignItems: "end", flexWrap: "wrap" }}>
        <FormControl size="sm" sx={{ minWidth: 130 }}>
          <FormLabel>Status</FormLabel>
          <Select
            value={statusFilter || null}
            onChange={(_, value) => {
              setStatusFilter(value || "");
              onFilterChangeResetPage();
            }}
            placeholder="All"
          >
            <Option value="">All</Option>
            <Option value="Available">Available</Option>
            <Option value="Rented">Rented</Option>
            <Option value="In Repair">In Repair</Option>
          </Select>
        </FormControl>
        <FormControl size="sm" sx={{ minWidth: 150 }}>
          <FormLabel>Brand</FormLabel>
          <Input
            value={brandFilter}
            onChange={(event) => setBrandFilter(event.target.value)}
            placeholder="e.g., Apple"
          />
        </FormControl>
        <FormControl size="sm">
          <FormLabel>From</FormLabel>
          <Input
            type="date"
            value={dateFromFilter}
            onChange={(event) => {
              setDateFromFilter(event.target.value);
              onFilterChangeResetPage();
            }}
          />
        </FormControl>
        <FormControl size="sm">
          <FormLabel>To</FormLabel>
          <Input
            type="date"
            value={dateToFilter}
            onChange={(event) => {
              setDateToFilter(event.target.value);
              onFilterChangeResetPage();
            }}
          />
        </FormControl>
        <Button size="sm" variant="outlined" color="neutral" onClick={onReset}>
          Reset
        </Button>
      </Stack>
    </Box>
  );
}
