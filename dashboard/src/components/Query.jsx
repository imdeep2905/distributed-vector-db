import React, { useState } from "react";
import {
  Input,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  Center,
  Heading,
  Box,
} from "@chakra-ui/react";

const Query = () => {
  const [query, setQuery] = useState("");
  const [nResults, setNResults] = useState(1);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const backendUrl = process.env.REACT_APP_BACKEND_URL || "";

  const handleQuery = () => {
    setLoading(true);

    // Mock POST request to /query endpoint
    fetch(backendUrl + "/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query_texts: [query],
        n_results: parseInt(nResults, 10),
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        setResults(
          data.ids.map((id, index) => {
            return {
              id: id,
              document: data.documents[index],
              metadata: data.metadatas[index],
              distance: data.distances[index],
            };
          })
        );
      })
      .catch((error) => console.error("Error fetching data:", error))
      .finally(() => setLoading(false));
  };

  return (
    <div>
      <Box p="4">
        <Heading mb="4" size="lg">
          Perform Similarity Search Query
        </Heading>
      </Box>
      <div>
        <Center>
          <Input
            placeholder="Enter query text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            mb="2"
            mt="4"
            w="75%"
          />
        </Center>
      </div>
      <div>
        <Center>
          <Input
            placeholder="Enter number of results"
            type="number"
            value={nResults}
            onChange={(e) => setNResults(e.target.value)}
            mb="2"
            w="75%"
          />
        </Center>
      </div>
      <div>
        <Center>
          <Button colorScheme="teal" onClick={handleQuery} mb="4">
            Query
          </Button>
        </Center>
      </div>
      <Table variant="striped" colorScheme="teal">
        <Thead>
          <Tr>
            <Th>ID</Th>
            <Th>Distance</Th>
            <Th>Document</Th>
            <Th>Metadata</Th>
          </Tr>
        </Thead>
        <Tbody>
          {loading ? (
            <Tr>
              <Td colSpan={4} textAlign="center">
                <Spinner size="lg" color="teal.500" />
              </Td>
            </Tr>
          ) : (
            results.map(
              (result, index) =>
                index < nResults && (
                  <Tr key={index}>
                    <Td>{result.id}</Td>
                    <Td>{result.distance}</Td>
                    <Td>{result.document}</Td>
                    <Td>{JSON.stringify(result.metadata)}</Td>
                  </Tr>
                )
            )
          )}
        </Tbody>
      </Table>
    </div>
  );
};

export default Query;
