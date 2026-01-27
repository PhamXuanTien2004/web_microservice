import { useForm } from '@mantine/form';
import { TextInput, PasswordInput, NumberInput, Button, Paper, Title, Grid, Select } from '@mantine/core';
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
        sensors: 1, // Mặc định là 1 thay vì 0 để hợp lệ ngay từ đầu
      },
    },

    // Thêm validation logic
    validate: {
      profile: {
        // Chỉ validate sensors khi role là 'user'
        sensors: (value, values) => 
          values.profile.role === 'user' && value < 1 
            ? 'Số lượng sensor phải ít nhất là 1' 
            : null,
        email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Email không hợp lệ'),
      },
    },
  });

  const handleRegister = async (values) => {
    try {
      // Nếu là admin, chúng ta có thể xóa field sensors trước khi gửi lên API nếu cần
      const payload = { ...values };
      if (payload.profile.role === 'admin') {
        payload.profile.sensors = 0; 
      }

      await authApi.post('/register', payload);
      alert("Đăng ký thành công!");
    } catch (error) {
      alert("Lỗi: " + (error.response?.data?.message || "Không thể kết nối Backend"));
    }
  };

  return (
    <Paper shadow="md" p="xl" withBorder className="max-w-2xl mx-auto mt-10">
      <Title order={2} mb="lg" ta="center">Đăng Ký Tài Khoản</Title>
      <form onSubmit={form.onSubmit(handleRegister)}>
        <Grid>
          <Grid.Col span={6}>
            <TextInput label="Username" {...form.getInputProps('username')} required />
            <PasswordInput label="Password" mt="md" {...form.getInputProps('password')} required />
          </Grid.Col>
          
          <Grid.Col span={6}>
            <TextInput label="Họ tên" {...form.getInputProps('profile.name')} />
            <TextInput label="Email" mt="xs" {...form.getInputProps('profile.email')} />
            <TextInput label="Điện thoại" mt="xs" {...form.getInputProps('profile.telphone')} />
            
            {/* Chuyển sang Select để giới hạn lựa chọn */}
            <Select 
              label="Role" 
              placeholder="Chọn vai trò"
              mt="xs"
              data={[
                { value: 'admin', label: 'Admin' },
                { value: 'user', label: 'User' },
              ]}
              {...form.getInputProps('profile.role')}
            />

            {/* Chỉ hiển thị Số Sensors nếu role là 'user' */}
            {form.values.profile.role === 'user' && (
              <NumberInput 
                label="Số Sensors" 
                mt="xs" 
                min={1} // Giới hạn ở UI
                {...form.getInputProps('profile.sensors')} 
              />
            )}
          </Grid.Col>
        </Grid>
        <Button type="submit" fullWidth mt="xl">Đăng ký ngay</Button>
      </form>
    </Paper>
  );
}