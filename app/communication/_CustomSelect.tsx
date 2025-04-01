// components/ui/select/index.tsx
import * as React from "react";
import {
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@radix-ui/react-icons";
import * as Select from "@radix-ui/react-select";

const CustomSelect = ({
  options,
  placeholder = "Select an option...",
  value,
  onValueChange,
  label,
  className = "",
}: any) => {
  return (
    <div className={className}>
      {label && <label className="mr-2 font-medium block mb-2">{label}</label>}
      <Select.Root  value={value} onValueChange={onValueChange}>
        <Select.Trigger
          className="inline-flex items-center justify-between rounded-md px-4 py-2 text-sm border border-gray-300 bg-white text-gray-800 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 w-full"
          aria-label={label || "Options"}
        >
          <Select.Value placeholder={placeholder} />
          <Select.Icon className="text-gray-500">
            <ChevronDownIcon />
          </Select.Icon>
        </Select.Trigger>
        <Select.Portal>
          <Select.Content
            className="overflow-hidden bg-white rounded-md shadow-lg border border-gray-200"
            position="popper"
          >
            <Select.ScrollUpButton className="flex items-center justify-center h-6 bg-white text-gray-700 cursor-default">
              <ChevronUpIcon />
            </Select.ScrollUpButton>
            <Select.Viewport className="p-1">
              {options.map((option: any) => (
                <Select.Item
                  key={option.value}
                  value={option.value || "_empty_"}
                  className="text-sm text-gray-800 rounded-md flex items-center h-8 px-4 py-2 relative select-none hover:bg-gray-100 data-[highlighted]:bg-gray-100 data-[highlighted]:outline-none"
                  disabled={option.disabled}
                >
                  <Select.ItemText>{option.label}</Select.ItemText>
                  <Select.ItemIndicator className="absolute right-2 inline-flex items-center">
                    <CheckIcon />
                  </Select.ItemIndicator>
                </Select.Item>
              ))}
            </Select.Viewport>
            <Select.ScrollDownButton className="flex items-center justify-center h-6 bg-white text-gray-700 cursor-default">
              <ChevronDownIcon />
            </Select.ScrollDownButton>
          </Select.Content>
        </Select.Portal>
      </Select.Root>
    </div>
  );
};

export { CustomSelect };