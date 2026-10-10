import React from "react";
import { AiCopilotWidget } from "@/components/ai-copilot-widget";

const MainLayout = ({ children }) => {
  return (
    <div className="container mx-auto my-32">
      {children}
      <AiCopilotWidget />
    </div>
  );
};

export default MainLayout;

