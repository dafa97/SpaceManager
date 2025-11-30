export type ReservationStatus = 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED';

export interface Reservation {
    id: number;
    space_id: number;
    user_id: number;
    start_time: string;
    end_time: string;
    total_price: number;
    status: ReservationStatus;
    notes?: string;
    created_at: string;
    updated_at: string;
}

export interface CreateReservationRequest {
    space_id: number;
    start_time: string;
    end_time: string;
    notes?: string;
}

export interface UpdateReservationRequest {
    start_time?: string;
    end_time?: string;
    status?: ReservationStatus;
    notes?: string;
}
