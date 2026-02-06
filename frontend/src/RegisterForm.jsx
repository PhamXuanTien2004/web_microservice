import { Link, useNavigate } from 'react-router-dom';
import { useForm } from '@mantine/form';
import { TextInput, PasswordInput, Button, Paper, Title, Container, Text, Select, NumberInput } from '@mantine/core';
import { authService } from './services/authService';

export function RegisterForm() {
  const navigate = useNavigate();

  const form = useForm({
    initialValues: {
      username: '',
      password: '',
      confirmPassword: '',
      email: '',
      name: '',
      telphone: '',
      role: 'user',
      sensors: 1,
      topic: '',
    },
    validate: {
      name: (value) => {
        if (!value) return 'Họ tên không được để trống';
        if (value.length < 2) return 'Họ tên phải có ít nhất 2 ký tự';
        return null;
      },
      email: (value) => {
        if (!value) return 'Email không được để trống';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Email không hợp lệ';
        return null;
      },
      telphone: (value) => {
        if (!value) return 'Số điện thoại không được để trống';
        if (!/^(84|0[3|5|7|8|9])+([0-9]{8})$/.test(value)) return 'Số điện thoại không hợp lệ (định dạng: 0xxxxxxxxx hoặc 84xxxxxxxxx)';
        return null;
      },
      username: (value) => {
        if (!value) return 'Username không được để trống';
        if (value.length < 3 || value.length > 50) return 'Username phải từ 3 đến 50 ký tự';
        return null;
      },
      password: (value) => {
        if (!value) return 'Password không được để trống';
        if (value.length < 8) return 'Password phải có ít nhất 8 ký tự';
        
        if (!/[A-Z]/.test(value)) return 'Password phải có ít nhất 1 chữ hoa';
        if (!/[a-z]/.test(value)) return 'Password phải có ít nhất 1 chữ thường';
        if (!/\d/.test(value)) return 'Password phải có ít nhất 1 số';
        if (!/[!@#$%^&*(),.?":{}|<>_\-+=[\]\\;/']/.test(value)) 
            return 'Password phải có ít nhất 1 ký tự đặc biệt';
        
        return null;
      },
      confirmPassword: (value, values) => {
        if (!value) return 'Vui lòng xác nhận password';
        if (value !== values.password) return 'Password không khớp';
        return null;
      },
      role: (value) => {
        if (!value) return 'Vui lòng chọn vai trò';
        return null;
      },
      sensors: (value, values) => {
        if (values.role === 'user') {
          if (!value || value < 1) return 'Số cảm biến phải ≥ 1';
        }
        return null;
      },
      topic: (value, values) => {
        if (values.role === 'user') {
          if (!value) return 'Tên topic không được để trống';
        }
        return null;
      },
    },
  });

  const handleRegister = async (values) => {
    try {
      const { confirmPassword, ...registerData } = values;
      
      // Backend yêu cầu cấu trúc: { username, password, profile: { name, email, telphone, role, sensors, topic } }
      const payload = {
        username: registerData.username,
        password: registerData.password,
        profile: {
          name: registerData.name,
          email: registerData.email,
          telphone: registerData.telphone,
          role: registerData.role,
          sensors: registerData.role === 'user' ? registerData.sensors : null,
          topic: registerData.role === 'user' ? registerData.topic : null,
        }
      };
      
      console.log('Sending register payload:', JSON.stringify(payload, null, 2));
      
      // Gọi API đăng ký
      const response = await authService.register(payload);
      
      alert("Đăng ký thành công! Vui lòng đăng nhập.");
      navigate('/auth/login');
      
    } catch (error) {
      console.error('Register error response:', error.response?.data);
      const errorMsg = error.response?.data?.errors 
        ? JSON.stringify(error.response.data.errors) 
        : error.response?.data?.error 
        ? error.response.data.error 
        : "Đã có lỗi xảy ra, vui lòng thử lại";
      alert("Lỗi đăng ký: " + errorMsg);
    }
  };

  return (
    <Container size={420} my={40}>
      <Title ta="center" className="font-bold">Tạo tài khoản mới</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Vui lòng nhập thông tin để đăng ký tài khoản
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={form.onSubmit(handleRegister)}>
          <TextInput 
            label="Họ tên" 
            placeholder="Tên đầy đủ của bạn" 
            required 
            {...form.getInputProps('name')} 
          />

          <TextInput 
            label="Email" 
            placeholder="Email của bạn" 
            required 
            mt="md"
            {...form.getInputProps('email')} 
          />

          <TextInput 
            label="Số điện thoại" 
            placeholder="Ví dụ: 0987654321 hoặc 84987654321"
            required 
            mt="md"
            {...form.getInputProps('telphone')} 
          />
          
          <TextInput 
            label="Username" 
            placeholder="Tên đăng nhập" 
            required 
            mt="md"
            {...form.getInputProps('username')} 
          />
          
          <PasswordInput 
            label="Password" 
            placeholder="Mật khẩu của bạn" 
            required 
            mt="md" 
            {...form.getInputProps('password')} 
          />

          <PasswordInput 
            label="Xác nhận Password" 
            placeholder="Nhập lại mật khẩu" 
            required 
            mt="md" 
            {...form.getInputProps('confirmPassword')} 
          />

          <Select 
            label="Vai trò" 
            placeholder="Chọn vai trò" 
            required 
            mt="md"
            data={[
              { value: 'user', label: 'User' },
              { value: 'admin', label: 'Admin' },
            ]}
            {...form.getInputProps('role')} 
          />

          {form.values.role === 'user' && (
            <>
              <NumberInput 
                label="Số cảm biến" 
                placeholder="Nhập số lượng cảm biến"
                min={1}
                required 
                mt="md"
                {...form.getInputProps('sensors')} 
              />

              <TextInput 
                label="Tên topic" 
                placeholder="Ví dụ: mqtt/sensor/data"
                required 
                mt="md"
                {...form.getInputProps('topic')} 
              />
            </>
          )}

          <Button type="submit" fullWidth mt="xl" color="blue">
            Đăng ký
          </Button>
          
          <Text ta="center" mt="md">
            Đã có tài khoản? <Link to="/auth/login">Đăng nhập</Link>
          </Text>
        </form>
      </Paper>
    </Container>
  );
}