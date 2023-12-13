import { HStack, Box } from "@chakra-ui/react";
import Health from "./components/Health.jsx";
import Query from "./components/Query.jsx";

function App() {
  return (
    <HStack height="100vh" width="100vw">
      <Box width="50%" height="100%" style={{ overflowY: "auto" }}>
        <Query />
      </Box>
      <Box width="2px" bg="gray.300" height="100%" />
      <Box width="50%" height="100%" style={{ overflowY: "auto" }}>
        <Health />
      </Box>
    </HStack>
  );
}

export default App;
