"use client";

import * as React from "react";
import { Check, ChevronsUpDown, PlusCircle } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
} from "@/components/ui/command";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";

type PopoverTriggerProps = React.ComponentPropsWithoutRef<typeof PopoverTrigger>;

interface TeamSwitcherProps extends PopoverTriggerProps { }

export default function OrgSelector({ className }: TeamSwitcherProps) {
    const [open, setOpen] = React.useState(false);
    const [selectedTeam, setSelectedTeam] = React.useState<any>(null);

    // Mock data for now
    const groups = [
        {
            label: "Personal Account",
            teams: [
                {
                    label: "Alicia Koch",
                    value: "personal",
                },
            ],
        },
        {
            label: "Teams",
            teams: [
                {
                    label: "Acme Inc.",
                    value: "acme-inc",
                },
                {
                    label: "Monsters Inc.",
                    value: "monsters",
                },
            ],
        },
    ];

    React.useEffect(() => {
        setSelectedTeam(groups[0].teams[0]);
    }, []);


    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    aria-label="Select a team"
                    className={cn("w-[200px] justify-between", className)}
                >
                    <Avatar className="mr-2 h-5 w-5">
                        <AvatarImage
                            src={`https://avatar.vercel.sh/${selectedTeam?.value}.png`}
                            alt={selectedTeam?.label}
                            className="grayscale"
                        />
                        <AvatarFallback>SC</AvatarFallback>
                    </Avatar>
                    {selectedTeam?.label}
                    <ChevronsUpDown className="ml-auto h-4 w-4 shrink-0 opacity-50" />
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[200px] p-0">
                <Command>
                    <CommandList>
                        <CommandInput placeholder="Search team..." />
                        <CommandEmpty>No team found.</CommandEmpty>
                        {groups.map((group) => (
                            <CommandGroup key={group.label} heading={group.label}>
                                {group.teams.map((team) => (
                                    <CommandItem
                                        key={team.value}
                                        onSelect={() => {
                                            setSelectedTeam(team);
                                            setOpen(false);
                                        }}
                                        className="text-sm"
                                    >
                                        <Avatar className="mr-2 h-5 w-5">
                                            <AvatarImage
                                                src={`https://avatar.vercel.sh/${team.value}.png`}
                                                alt={team.label}
                                                className="grayscale"
                                            />
                                            <AvatarFallback>SC</AvatarFallback>
                                        </Avatar>
                                        {team.label}
                                        <Check
                                            className={cn(
                                                "ml-auto h-4 w-4",
                                                selectedTeam?.value === team.value
                                                    ? "opacity-100"
                                                    : "opacity-0"
                                            )}
                                        />
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        ))}
                    </CommandList>
                    <CommandSeparator />
                    <CommandList>
                        <CommandGroup>
                            <CommandItem>
                                <PlusCircle className="mr-2 h-5 w-5" />
                                Create Team
                            </CommandItem>
                        </CommandGroup>
                    </CommandList>
                </Command>
            </PopoverContent>
        </Popover>
    );
}

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
