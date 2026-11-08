import React from "react";
import { AlertTriangle, PhoneCall } from "lucide-react";

interface EmergencyCardProps {
  message?: string;
  callLabel?: string;
}

export const EmergencyCard: React.FC<EmergencyCardProps> = ({
  message = "This may be a medical emergency. Go to the nearest hospital immediately or call 108. Do not wait for an online answer.",
  callLabel = "Call 108 Emergency Helpline",
}) => {
  return (
    <div
      role="alert"
      className="p-5 my-4 bg-red-600 dark:bg-red-700 text-white rounded-xl shadow-lg border-2 border-red-800 focus:outline-none focus:ring-4 focus:ring-red-400"
      aria-label="Medical emergency warning"
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-8 h-8 flex-shrink-0 text-amber-300 animate-pulse" aria-hidden="true" />
        <div className="space-y-3">
          <h2 className="text-xl font-bold tracking-tight">URGENT MEDICAL NOTICE</h2>
          <p className="text-base leading-relaxed font-medium text-red-50">{message}</p>
          <div>
            <a
              href="tel:108"
              className="inline-flex items-center gap-2 px-5 py-3 bg-white text-red-700 font-bold text-lg rounded-lg shadow hover:bg-red-50 focus:outline-none focus:ring-4 focus:ring-white transition"
              aria-label={callLabel}
            >
              <PhoneCall className="w-6 h-6 text-red-600" aria-hidden="true" />
              <span>{callLabel}</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
