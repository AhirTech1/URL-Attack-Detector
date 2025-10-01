
import React from 'react';
import type { DetectionResult } from '../types';
import { FingerprintIcon, TerminalIcon, ListChecksIcon, ShieldAlertIcon } from './icons';

interface DetectionDetailsProps {
  detection: DetectionResult;
}

const DetailItem: React.FC<{ label: string; value: React.ReactNode; mono?: boolean }> = ({ label, value, mono = false }) => (
    <div>
        <p className="text-sm font-medium text-text-secondary">{label}</p>
        <p className={`text-text-primary ${mono ? 'font-mono' : ''}`}>{value}</p>
    </div>
);


export const DetectionDetails: React.FC<DetectionDetailsProps> = ({ detection }) => {
    const confidencePercentage = (detection.confidence * 100).toFixed(1);

    return (
        <div className="p-6 bg-surface animate-fade-in-right">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                
                {/* General Info */}
                <div className="space-y-4">
                    <h4 className="flex items-center text-lg font-semibold text-text-primary">
                        <FingerprintIcon className="w-5 h-5 mr-2 text-accent" />
                        General Information
                    </h4>
                    <DetailItem label="ID" value={detection.id} mono />
                    <DetailItem label="Timestamp" value={new Date(detection.timestamp).toLocaleString()} />
                    <DetailItem label="Source IP" value={detection.src_ip} mono />
                    <DetailItem label="Host" value={detection.host} mono />
                </div>
                
                {/* Attack Details */}
                <div className="space-y-4">
                    <h4 className="flex items-center text-lg font-semibold text-text-primary">
                        <ShieldAlertIcon className="w-5 h-5 mr-2 text-accent" />
                        Attack Details
                    </h4>
                    <DetailItem label="Attack Prediction" value={<span className="font-bold text-red-400">{detection.attack_prediction}</span>} />
                    <DetailItem label="Confidence" value={
                        <div className="flex items-center">
                            <span className="font-bold text-lg mr-2">{confidencePercentage}%</span>
                            <div className="w-full bg-primary rounded-full h-2.5">
                                <div className="bg-red-500 h-2.5 rounded-full" style={{ width: `${confidencePercentage}%` }}></div>
                            </div>
                        </div>
                    }/>
                    <DetailItem label="Rule Matched" value={detection.rule_matched ? <span className="px-2 py-1 bg-yellow-800/50 text-yellow-300 rounded-full text-xs font-mono">{detection.rule_matched}</span> : 'N/A'} />
                    <DetailItem label="Attack Succeeded" value={detection.success_flag ? <span className="font-bold text-red-400">Yes</span> : 'No'} />
                </div>

                {/* URI & Payload */}
                <div className="space-y-4 lg:col-span-1 md:col-span-2">
                     <h4 className="flex items-center text-lg font-semibold text-text-primary">
                        <TerminalIcon className="w-5 h-5 mr-2 text-accent" />
                        Full URI & Payload
                    </h4>
                    <div className="bg-primary p-3 rounded-md">
                        <p className="font-mono text-sm text-text-secondary break-all">{detection.uri}</p>
                    </div>
                    <div>
                         <p className="text-sm font-medium text-text-secondary">Payload Analysis (Mock)</p>
                         <p className="text-text-primary text-sm italic">Decoded payload appears to contain a common SQL injection pattern targeting the 'id' parameter.</p>
                    </div>
                </div>

                {/* Suggested Actions - Spans full width on medium screens */}
                <div className="space-y-2 md:col-span-2 lg:col-span-3">
                    <h4 className="flex items-center text-lg font-semibold text-text-primary">
                        <ListChecksIcon className="w-5 h-5 mr-2 text-accent" />
                        Suggested Actions
                    </h4>
                     <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
                        <li>Block the source IP <strong className="font-mono text-text-primary">{detection.src_ip}</strong> at the firewall.</li>
                        <li>Investigate other activities from this IP address around the time of the event.</li>
                        <li>Patch the vulnerable application or apply input sanitization to prevent this attack vector.</li>
                        <li>If the attack was successful, initiate incident response procedures.</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};
