const hre = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("Deploying ThreatIntelligence contract...");

  const ThreatIntelligence = await hre.ethers.getContractFactory("ThreatIntelligence");
  const contract = await ThreatIntelligence.deploy();

  await contract.waitForDeployment();
  const contractAddress = await contract.getAddress();

  console.log("ThreatIntelligence deployed to:", contractAddress);

  // Save contract address and ABI for Python backend
  const contractInfo = {
    address: contractAddress,
    abi: JSON.parse(contract.interface.formatJson())
  };

  fs.writeFileSync("contract_info.json", JSON.stringify(contractInfo, null, 2));
  console.log("Contract info saved to contract_info.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });