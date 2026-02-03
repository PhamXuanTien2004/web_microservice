import React, { useState, useEffect } from 'react';
import { MantineProvider, Container, Group, Button, Avatar, Text, Card, Box } from '@mantine/core';
import { authService } from './services/authService';
import { userService } from './services/userService';
import { LoginForm } from './LoginForm';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => { checkLoginStatus(); }, []);

  const checkLoginStatus = async () => {
    try {
      const resp = await userService.getMyProfile();
      setUser(resp.data.data);
    } catch (err) {
      setUser(null);
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setUser(null);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <MantineProvider withGlobalStyles withNormalizeCSS>
      <Box px="md" py="sm" sx={{ borderBottom: '1px solid #eee' }}>
        <Group position="apart">
          <Text weight={700}>My Microservices App</Text>
          <Group>
            {user ? (
              <Group>
                <Avatar radius="xl">{user.name ? user.name.charAt(0).toUpperCase() : 'U'}</Avatar>
                <Text>{user.name}</Text>
                <Button variant="outline" onClick={handleLogout}>Logout</Button>
              </Group>
            ) : null}
          </Group>
        </Group>
      </Box>

      <Container size="sm" mt="md">
        {!user ? (
          <Card shadow="sm" p="lg" radius="md">
            <LoginForm onSuccess={checkLoginStatus} />
          </Card>
        ) : (
          <Card shadow="sm" p="lg" radius="md">
            <Text size="xl" weight={700}>Xin chào, {user.name}</Text>
            <Text color="dimmed">Email: {user.email}</Text>
            <Text mt="md">Role: {user.role}</Text>
          </Card>
        )}
      </Container>
    </MantineProvider>
  );
}

export default App;