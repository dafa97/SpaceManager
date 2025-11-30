export type SpaceType = 'hourly' | 'daily' | 'monthly';

export interface Space {
    id: number;
    name: string;
    description?: string;
    space_type: SpaceType;
    capacity?: number;
    price_per_unit: number;
    is_available: boolean;
    floor?: string;
    area_sqm?: number;
    created_at: string;
    updated_at: string;
}

export interface CreateSpaceRequest {
    name: string;
    description?: string;
    space_type: SpaceType;
    capacity?: number;
    price_per_unit: number;
    is_available?: boolean;
    floor?: string;
    area_sqm?: number;
}

export interface UpdateSpaceRequest {
    name?: string;
    description?: string;
    space_type?: SpaceType;
    capacity?: number;
    price_per_unit?: number;
    is_available?: boolean;
    floor?: string;
    area_sqm?: number;
}
