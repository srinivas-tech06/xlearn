import { useApp } from '../../context/AppContext';

export default function XPNotification() {
  const { state } = useApp();
  const { xpNotification } = state;

  if (!xpNotification) return null;

  return (
    <div className="xp-notification">
      ⚡ +{xpNotification} XP
    </div>
  );
}
