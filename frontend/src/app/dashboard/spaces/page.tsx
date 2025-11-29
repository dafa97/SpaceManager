"use client";

import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { spacesApi } from "@/lib/api";
import { Space } from "@/types/space";

export default function SpacesPage() {
    const [spaces, setSpaces] = useState<Space[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSpaces = async () => {
            try {
                const data = await spacesApi.list();
                setSpaces(data);
            } catch (error) {
                console.error("Failed to fetch spaces:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchSpaces();
    }, []);

    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Spaces</h2>
                <div className="flex items-center space-x-2">
                    <Button asChild>
                        <Link href="/dashboard/spaces/new">
                            <Plus className="mr-2 h-4 w-4" /> Add Space
                        </Link>
                    </Button>
                </div>
            </div>
            <Card>
                <CardHeader>
                    <CardTitle>All Spaces</CardTitle>
                    <CardDescription>
                        Manage your rental spaces here.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div>Loading...</div>
                    ) : spaces.length === 0 ? (
                        <div className="text-center py-10 text-muted-foreground">
                            No spaces found. Create your first space to get started.
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {spaces.map((space) => (
                                <div
                                    key={space.id}
                                    className="flex items-center justify-between p-4 border rounded-lg"
                                >
                                    <div>
                                        <h3 className="font-medium">{space.name}</h3>
                                        <p className="text-sm text-muted-foreground">
                                            Capacity: {space.capacity} • ${space.price_per_hour}/hr
                                        </p>
                                    </div>
                                    <Button variant="outline" asChild>
                                        <Link href={`/dashboard/spaces/${space.id}`}>View</Link>
                                    </Button>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
