export interface Log {
    filename: string;
    filesize: number;
    line_count: number;
    created_at?: Date | null;
    updated_at?: Date | null;
}