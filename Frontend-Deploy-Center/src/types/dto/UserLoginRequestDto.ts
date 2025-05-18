export interface UserLoginRequestDto {
  identifier: string;
  credential: string;
  two_factor_code: string | null;
}
