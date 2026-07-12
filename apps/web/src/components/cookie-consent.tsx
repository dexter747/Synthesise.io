"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Cookies from "js-cookie";
import { motion, AnimatePresence } from "framer-motion";
import { X, Cookie, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";

const CONSENT_COOKIE_NAME = "synthesize_cookie_consent";
const CONSENT_VERSION = "1.0";

interface CookiePreferences {
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
  functional: boolean;
}

const defaultPreferences: CookiePreferences = {
  necessary: true, // Always required
  analytics: false,
  marketing: false,
  functional: false,
};

export function CookieConsent() {
  const [showBanner, setShowBanner] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>(defaultPreferences);

  useEffect(() => {
    // Check if user has already given consent
    const consent = Cookies.get(CONSENT_COOKIE_NAME);
    if (!consent) {
      // Small delay for better UX
      const timer = setTimeout(() => setShowBanner(true), 1500);
      return () => clearTimeout(timer);
    } else {
      try {
        const parsed = JSON.parse(consent);
        setPreferences(parsed.preferences || defaultPreferences);
      } catch {
        setShowBanner(true);
      }
    }
  }, []);

  const savePreferences = (prefs: CookiePreferences) => {
    const consentData = {
      version: CONSENT_VERSION,
      timestamp: new Date().toISOString(),
      preferences: prefs,
    };
    
    Cookies.set(CONSENT_COOKIE_NAME, JSON.stringify(consentData), {
      expires: 365, // 1 year
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
    });
    
    setPreferences(prefs);
    setShowBanner(false);
    setShowPreferences(false);
    
    // Apply preferences (e.g., load/block analytics scripts)
    applyPreferences(prefs);
  };

  const applyPreferences = (prefs: CookiePreferences) => {
    // Here you would enable/disable various tracking scripts
    // For example:
    if (prefs.analytics) {
      // Enable Google Analytics, Mixpanel, etc.
      console.log("Analytics enabled");
    }
    if (prefs.marketing) {
      // Enable marketing pixels, etc.
      console.log("Marketing cookies enabled");
    }
  };

  const acceptAll = () => {
    savePreferences({
      necessary: true,
      analytics: true,
      marketing: true,
      functional: true,
    });
  };

  const rejectAll = () => {
    savePreferences({
      necessary: true,
      analytics: false,
      marketing: false,
      functional: false,
    });
  };

  const saveCustomPreferences = () => {
    savePreferences(preferences);
  };

  return (
    <>
      {/* Cookie Banner */}
      <AnimatePresence>
        {showBanner && (
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed bottom-4 left-4 right-4 z-50 md:left-auto md:right-6 md:max-w-lg"
          >
            <div className="bg-zinc-900/95 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-teal-500/20 flex items-center justify-center flex-shrink-0">
                  <Cookie className="w-5 h-5 text-teal-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-white mb-2">
                    Cookie Preferences
                  </h3>
                  <p className="text-sm text-zinc-400 mb-4">
                    We use cookies to enhance your experience, analyze site traffic, and for marketing purposes. 
                    By clicking "Accept All", you consent to our use of cookies.{" "}
                    <Link href="/legal/cookies" className="text-teal-400 hover:text-teal-300">
                      Learn more
                    </Link>
                  </p>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Button
                      variant="gradient"
                      size="sm"
                      onClick={acceptAll}
                      className="flex-1"
                    >
                      Accept All
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={rejectAll}
                      className="flex-1 border-white/10 text-white hover:bg-white/5"
                    >
                      Reject All
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowPreferences(true)}
                      className="text-zinc-400 hover:text-white"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Customize
                    </Button>
                  </div>
                </div>
                <button
                  onClick={rejectAll}
                  className="p-1 rounded-lg text-zinc-500 hover:text-white hover:bg-white/10 transition-colors"
                  aria-label="Close"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Preferences Dialog */}
      <Dialog open={showPreferences} onOpenChange={setShowPreferences}>
        <DialogContent className="sm:max-w-lg bg-zinc-900 border-white/10">
          <DialogHeader>
            <DialogTitle className="text-white">Cookie Preferences</DialogTitle>
            <DialogDescription className="text-zinc-400">
              Manage your cookie preferences below. Note that disabling certain cookies may affect your experience.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6 py-4">
            {/* Necessary Cookies */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-sm font-medium text-white">Necessary Cookies</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  Required for the website to function properly. Cannot be disabled.
                </p>
              </div>
              <Switch checked={true} disabled />
            </div>

            {/* Analytics Cookies */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-sm font-medium text-white">Analytics Cookies</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  Help us understand how visitors interact with our website.
                </p>
              </div>
              <Switch
                checked={preferences.analytics}
                onCheckedChange={(checked) =>
                  setPreferences({ ...preferences, analytics: checked })
                }
              />
            </div>

            {/* Functional Cookies */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-sm font-medium text-white">Functional Cookies</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  Enable enhanced functionality and personalization.
                </p>
              </div>
              <Switch
                checked={preferences.functional}
                onCheckedChange={(checked) =>
                  setPreferences({ ...preferences, functional: checked })
                }
              />
            </div>

            {/* Marketing Cookies */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-sm font-medium text-white">Marketing Cookies</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  Used to deliver relevant advertisements and track campaign performance.
                </p>
              </div>
              <Switch
                checked={preferences.marketing}
                onCheckedChange={(checked) =>
                  setPreferences({ ...preferences, marketing: checked })
                }
              />
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => setShowPreferences(false)}
              className="flex-1 border-white/10 text-white hover:bg-white/5"
            >
              Cancel
            </Button>
            <Button
              variant="gradient"
              onClick={saveCustomPreferences}
              className="flex-1"
            >
              Save Preferences
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
