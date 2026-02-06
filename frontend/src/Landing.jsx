import React from 'react';
import { Container, Paper, Title, Text, Button, Center, Stack, Box } from '@mantine/core';
import { Link } from 'react-router-dom';

export function Landing() {
  return (
    <Box
      sx={(theme) => ({
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: theme.colors.gray[0],
      })}
    >
      <Container size={400}>
        <Paper shadow="md" p={50} radius="md" withBorder>
          <Center mb="lg">
            <div>
              <Title order={1} ta="center" mb="xs">My Microservices</Title>
              <Text ta="center" c="dimmed" size="sm">Quản lý hệ thống IoT của bạn</Text>
            </div>
          </Center>

          <Stack gap="md" mt={40}>
            <Button
              component={Link}
              to="/auth/login"
              size="lg"
              fullWidth
              color="blue"
            >
              Đăng Nhập
            </Button>

            <Button
              component={Link}
              to="/auth/register"
              size="lg"
              fullWidth
              variant="outline"
              color="blue"
            >
              Đăng Ký
            </Button>
          </Stack>

          <Text ta="center" size="xs" c="dimmed" mt={30}>
            © 2026 My Microservices. Bảo vệ bởi JWT & Token.
          </Text>
        </Paper>
      </Container>
    </Box>
  );
}
