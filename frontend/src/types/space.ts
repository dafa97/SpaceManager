export interface Space {
    id: string;
    organization_id: string;
    name: string;
    description?: string;
    capacity: number;
    price_per_hour: number;
    amenities?: string[];
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface CreateSpaceRequest {
    name: string;
    description?: string;
    capacity: number;
    price_per_hour: number;
    amenities?: string[];
}

export interface UpdateSpaceRequest {
    name?: string;
    description?: string;
    capacity?: number;
    price_per_hour?: number;
    amenities?: string[];
    is_active?: boolean;
}
