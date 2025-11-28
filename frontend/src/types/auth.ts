export interface User {
    id: number;
    email: string;
    full_name?: string;
    is_active: boolean;
    is_superuser: boolean;
    created_at: string;
    updated_at: string;
}

export interface Organization {
    id: number;
    name: string;
    slug: string;
    is_active: boolean;
    created_at: string;
}

export interface OrganizationMembership {
    organization: Organization;
    role: string;
    status: string;
    created_at: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    full_name?: string;
    organization_name: string;
    organization_slug: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}
