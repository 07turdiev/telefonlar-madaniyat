export interface Employee {
  id: number
  department_id: number
  full_name: string
  position: string
  room: string
  internal_phone: string
  city_phone: string
  mobile_phone: string
  email: string
  sort_order: number
  updated_at: string
}

export type EmployeeInput = Omit<Employee, 'id' | 'sort_order' | 'updated_at' | 'department_id'> & {
  department_id: number | null
}

export interface Department {
  id: number
  name: string
  parent_id: number | null
  sort_order: number
  level: 0 | 1
}

export interface Section extends Department {
  employees: Employee[]
}

export interface DepartmentWithCount extends Department {
  count: number
}

export interface Directory {
  org_name: string
  site_title: string
  updated: string | null
  sections: Section[]
}

export interface User {
  id: number
  username: string
  full_name: string
  is_admin: boolean
  created_at: string
}

export interface LogEntry {
  id: number
  at: string
  username: string
  action: string
  details: string
}
