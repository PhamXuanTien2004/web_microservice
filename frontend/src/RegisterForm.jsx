import { useForm } from '@mantine/form';
import { TextInput, PasswordInput, NumberInput, Button, Paper, Title, Grid, Select, Stack } from '@mantine/core';
import { authApi } from './api';

export function RegisterForm() {
  const form = useForm({
    initialValues: {
      username: '',
      password: '',
      profile: {
        name: '',
        email: '',
        telphone: '',
        role: '',
        topic: '',
        sensors: 1,
      },
    },

    validate: {
      username: (value) => (value.length < 3 ? 'Username quá ngắn' : null),
      // Cảnh báo: Backend yêu cầu password mạnh (Hoa, thường, số, ký tự đặc biệt)
      password: (value) => (value.length < 8 ? 'Mật khẩu phải ít nhất 8 ký tự' : null),
      profile: {
        email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Email không hợp lệ'),
        // Đảm bảo đúng tên telphone ở đây
        telphone: (value) => (/^(0|84)[3|5|7|8|9][0-9]{8}$/.test(value) ? null : 'Số điện thoại không hợp lệ'),
      },
    },
  });

  const handleRegister = async (values) => {
    try {
      const payload = JSON.parse(JSON.stringify(values));

      // Nếu là admin, xóa hẳn 2 trường này để Backend gán mặc định là None/Null
      if (payload.profile.role === 'admin') {
        delete payload.profile.sensors;
        delete payload.profile.topic;
      }

      await authApi.post('/register', payload);
      alert("Đăng ký thành công!");
      form.reset();
    } catch (error) {
      const backendErrors = error.response?.data?.errors;
      
      if (backendErrors) {
        // Kiểm tra xem lỗi có nằm ở username không
        if (backendErrors.username) {
          alert("Lỗi: " + backendErrors.username[0]); // Sẽ hiển thị "Username đã tồn tại"
        } else {
          alert("Lỗi dữ liệu: " + JSON.stringify(backendErrors));
        }
      } else {
        alert("Lỗi kết nối Backend");
      }
    }
  };

  return (
    <Paper shadow="md" p="xl" withBorder className="max-w-2xl mx-auto mt-10">
      <Title order={2} mb="lg" ta="center">Đăng Ký Tài Khoản</Title>
      
      <form onSubmit={form.onSubmit(handleRegister)}>
        <Grid gutter="md">
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Stack>
              <TextInput label="Username" {...form.getInputProps('username')} required />
              <PasswordInput label="Password" description="Gồm chữ hoa, thường, số và ký tự đặc biệt" {...form.getInputProps('password')} required />
            </Stack>
          </Grid.Col>
          
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Stack gap="xs">
              <TextInput label="Họ tên" {...form.getInputProps('profile.name')} required />
              <TextInput label="Email" {...form.getInputProps('profile.email')} required />
              {/* Sửa từ telephone thành telphone ở đây */}
              <TextInput label="Điện thoại" {...form.getInputProps('profile.telphone')} required />
              
              <Select 
                label="Role" 
                data={[
                  { value: 'admin', label: 'Admin' },
                  { value: 'user', label: 'User' },
                ]}
                {...form.getInputProps('profile.role')}
              />

              {form.values.profile.role === 'user' && (
                <>
                  <NumberInput 
                    label="Số Sensors" 
                    min={1} 
                    {...form.getInputProps('profile.sensors')} 
                  />
                  <TextInput 
                    label="Topic" 
                    placeholder="mqtt/topic/path"
                    {...form.getInputProps('profile.topic')} 
                  />
                </>
              )}
            </Stack>
          </Grid.Col>
        </Grid>
        
        <Button type="submit" fullWidth mt="xl" size="md">
          Đăng ký ngay
        </Button>
      </form>
    </Paper>
  );
}