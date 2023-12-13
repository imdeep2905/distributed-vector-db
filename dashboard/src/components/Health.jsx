import React, { useState, useEffect } from "react";
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Box,
  Button,
  Spinner,
  Heading,
} from "@chakra-ui/react";

const TableComponent = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const backendUrl = process.env.REACT_APP_BACKEND_URL || "";

  const fetchData = () => {
    setLoading(true);
    fetch(backendUrl + "/health")
      .then((response) => response.json())
      .then((result) => setData(result))
      .catch((error) => console.error("Error fetching data:", error))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, []); // Fetch data on component mount

  return (
    <Box p="4">
      <Heading mb="4" size="lg">
        Health of DB Containers
      </Heading>
      <Button mb="4" onClick={fetchData} isLoading={loading}>
        Refresh
      </Button>
      <Table variant="striped" colorScheme="teal">
        <Thead>
          <Tr>
            <Th>Address</Th>
            <Th>Used RAM (MB)</Th>
            <Th>Total RAM (MB)</Th>
            <Th>CPU Usage (%)</Th>
            <Th>Average Response Time (ms)</Th>
          </Tr>
        </Thead>
        <Tbody>
          {loading ? (
            <Tr>
              <Td colSpan={5} textAlign="center">
                <Spinner size="lg" color="teal.500" />
              </Td>
            </Tr>
          ) : (
            data.map((item) => (
              <Tr key={item.key}>
                <Td>{item.address}</Td>
                <Td>{item.used_ram}</Td>
                <Td>{item.total_ram}</Td>
                <Td>{item.used_cpu}</Td>
                <Td>{item.avg_response_time}</Td>
              </Tr>
            ))
          )}
        </Tbody>
      </Table>
    </Box>
  );
};

export default TableComponent;
