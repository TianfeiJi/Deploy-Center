export interface HttpResult<T> {
  code?: number;
  status: string;
  msg: string;
  data: T;
}
