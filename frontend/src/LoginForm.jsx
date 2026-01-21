import { Link, useNavigate } from 'react-router-dom';
import { useForm } from '@mantine/form';
import { TextInput, PasswordInput, Button, Paper, Title, Container, Text } from '@mantine/core';
import { authApi } from "./api"; // Đã sửa từ ./app thành ./api theo thảo luận trước

export function LoginForm() {
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

  // Đặt hàm handleLogin ra ngoài useForm
  const handleLogin = async (values) => {
    try {
      // Gửi yêu cầu tới Flask Auth Service (Port 5001)
      const response = await authApi.post('/login', values);
      
      // Lưu thông tin vào LocalStorage
      // Lưu ý: Kiểm tra key trả về từ Flask của bạn (token hoặc access_token)
      localStorage.setItem('user_token', response.data.token || response.data.access_token);
      localStorage.setItem('username', values.username);

      alert("Chào mừng " + values.username + " đã quay trở lại!");

      // Chuyển hướng sang trang profile
      navigate('/profile'); 
    } catch (error) {
      const errorMsg = error.response?.data?.message || "Sai username hoặc password";
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
            Chưa có tài khoản? <Link to="/register" style={{ color: 'blue' }}>Đăng ký ngay</Link>
          </Text>
        </form>
      </Paper>
    </Container>
  );
}