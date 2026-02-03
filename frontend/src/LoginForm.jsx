import { Link, useNavigate } from 'react-router-dom';
import { useForm } from '@mantine/form';
import { TextInput, PasswordInput, Button, Paper, Title, Container, Text } from '@mantine/core';
import { authService } from './services/authService';

export function LoginForm({ onSuccess }) {
  const navigate = useNavigate();

  const form = useForm({
    initialValues: {
      username: '',
      password: '',
    },
    // Đồng bộ Validation với Backend Flask/Marshmallow
    validate: {
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
    },
  });

  const handleLogin = async (values) => {
    try {
      // 1. Gửi yêu cầu đăng nhập
      const response = await authService.login(values.username, values.password);
      
      // 2. Chỉ lưu các thông tin không nhạy cảm (như username) để hiển thị giao diện
      // Token đã được trình duyệt tự quản lý trong Cookie HttpOnly
      localStorage.setItem('username', response.data.user.username);
      localStorage.setItem('is_active', response.data.user.is_active);

      // Gọi callback onSuccess nếu được cung cấp để parent cập nhật
      if (onSuccess) await onSuccess();

      alert("Chào mừng " + response.data.user.username + " đã quay trở lại!");

      // 3. Điều hướng nội bộ trong React App
      navigate('/user/profile'); 
      
    } catch (error) {
      // Khớp với key "error" trả về từ Flask
      const errorMsg = error.response?.data?.error || "Đã có lỗi xảy ra, vui lòng thử lại";
      alert("Lỗi đăng nhập: " + errorMsg);
    }
  };

  return (
    <Container size={420} my={40}>
      <Title ta="center" className="font-bold">Chào mừng trở lại!</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Vui lòng nhập thông tin để đăng nhập hệ thống
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={form.onSubmit(handleLogin)}>
          <TextInput 
            label="Username" 
            placeholder="Tên đăng nhập của bạn" 
            required 
            {...form.getInputProps('username')} 
          />
          
          <PasswordInput 
            label="Password" 
            placeholder="Mật khẩu của bạn" 
            required 
            mt="md" 
            {...form.getInputProps('password')} 
          />

          <Button type="submit" fullWidth mt="xl" color="blue">
            Đăng nhập
          </Button>
          
          <Text ta="center" mt="md">
            Chưa có tài khoản? <Link to="/auth/register">Đăng ký ngay</Link>
          </Text>
        </form>
      </Paper>
    </Container>
  );
}