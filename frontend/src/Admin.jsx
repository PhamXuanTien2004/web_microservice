import React, { useState } from 'react';
import { Container, Title, Button, Textarea, TextInput, Select, Group, Stack } from '@mantine/core';
import { api } from './App';

export default function Admin() {
  const [output, setOutput] = useState('');
  const [endpoint, setEndpoint] = useState('/user/profile');
  const [method, setMethod] = useState('GET');
  const [body, setBody] = useState('');

  const callEndpoint = async () => {
    try {
      setOutput('Loading...');
      const cfg = { method, url: endpoint };

      if (method === 'GET' || method === 'DELETE') {
        const resp = await api.request(cfg);
        setOutput(JSON.stringify(resp.data, null, 2));
        return;
      }

      // POST / PUT
      cfg.data = body ? JSON.parse(body) : {};
      const resp = await api.request(cfg);
      setOutput(JSON.stringify(resp.data, null, 2));
    } catch (err) {
      const msg = err.response?.data || err.message || String(err);
      setOutput(typeof msg === 'string' ? msg : JSON.stringify(msg, null, 2));
    }
  };

  return (
    <Container size="md" my={40}>
      <Title order={2} mb="md">Admin: API Explorer (via Gateway)</Title>

      <Stack>
        <Group>
          <Select
            value={method}
            onChange={setMethod}
            data={["GET", "POST", "PUT", "DELETE"]}
            style={{ width: 120 }}
          />

          <TextInput
            placeholder="/user/profile or /auth/login"
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            sx={{ flex: 1 }}
          />

          <Button onClick={callEndpoint}>Send</Button>
        </Group>

        <Textarea
          minRows={10}
          placeholder='Request body as JSON (for POST/PUT)'
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />

        <Title order={4}>Response</Title>
        <Textarea minRows={10} readOnly value={output} />
      </Stack>
    </Container>
  );
}
