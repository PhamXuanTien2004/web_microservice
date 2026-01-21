import { useForm } from '@mantine/form';
import { TextInput, PasswordInput, NumberInput, Button, Paper, Title, Grid } from '@mantine/core';
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
        role: 'admin',
        sensors: 0,
      },
    },
  });

  const handleRegister = async (values) => {
    try {
      const response = await authApi.post('/register', values);
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
            <NumberInput label="Số Sensors" mt="xs" {...form.getInputProps('profile.sensors')} />
          </Grid.Col>
        </Grid>
        <Button type="submit" fullWidth mt="xl">Đăng ký ngay</Button>
      </form>
    </Paper>
  );
}